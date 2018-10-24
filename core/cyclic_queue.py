import logging
from multiprocessing import Lock

from core.nico_object_factory import NicoObjectFactory
from core.repeated_timer import RepeatedTimer
from core.video import Video
from indexer.indexer_service import Indexer

log = logging.getLogger(__name__)

k_MAX_QUEUE_SIZE = 100
k_MAX_RETRY = 3


class QueueElement:
    def __init__(self, video):
        self.video = video
        self.is_available = True
        self.trials_remaining = 1 + k_MAX_RETRY

    def __str__(self):
        return self.video.video_id


class CyclicQueue:
    def __init__(self, indexer=None):
        self._lock = Lock()
        self._list = []
        self.indexer = indexer
        self.replenish_timer = RepeatedTimer(30, self.pull_from_indexer)

    def pull_from_indexer(self):
        log.debug('pull_from_indexer len(queue)={}'.format(len(self._list)))

        if len(self._list) > k_MAX_QUEUE_SIZE // 10:
            log.debug('exiting pull_from_indexer because the local queue is sufficiently big')
            return

        pending = self.indexer.get_video_ids_by_status(Indexer.k_STATUS_PENDING,
                                                       max_result_set_size=k_MAX_QUEUE_SIZE // 2)
        login_failed = self.indexer.get_video_ids_by_status(Indexer.k_STATUS_LOGIN_REQUIRED,
                                                            max_result_set_size=k_MAX_QUEUE_SIZE // 2)

        self._append_all(pending)
        self._append_all(login_failed, requires_creds=True)

    def _append_all(self, video_ids, requires_creds=False):
        log.debug('_append_all len(video_ids)={} requires_creds={}'.format(len(video_ids), str(requires_creds)))
        self._lock.acquire()
        existing_video_ids = {}
        for qe in self._list:
            existing_video_ids[str(qe)] = None
        for new_video_id in video_ids:
            if new_video_id not in existing_video_ids:
                video = Video(video_id=new_video_id)
                video.requires_creds = requires_creds
                qe = QueueElement(video=video)
                self._list.append(qe)
        self._lock.release()

    def enqueue(self, video=None, url=None, parent_video=None):
        if (1 if video else 0) + (1 if url else 0) != 1:
            AssertionError('Only one parameter allowed')

        if url:
            videos = NicoObjectFactory(url=url).get_videos()
        else:
            videos = [video]

        self._lock.acquire()
        for video in videos:
            parent_str = '' if not parent_video else ' (Parent: {})'.format(parent_video)
            exists = self.indexer.exists(video_id=video.video_id)
            if not exists:
                if len(self._list) <= k_MAX_QUEUE_SIZE:
                    self._list.append(QueueElement(video))
                self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_PENDING)
                log.info('Enqueued:      {}{}'.format(video.video_id, parent_str))
            else:
                log.info('Duplicate:     {}{}'.format(video.video_id, parent_str))
        self._lock.release()

    def peek_and_reserve(self):
        self._lock.acquire()

        to_return = None
        for qe in self._list:
            if qe.is_available:
                qe.is_available = False
                qe.trials_remaining -= 1
                to_return = qe.video
                break

        self._lock.release()

        return to_return

    def mark_as_done(self, video):
        self._lock.acquire()
        self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_DONE)
        qe = self.get_qe_by_video_id(video.video_id)
        self._list.remove(qe)
        self._lock.release()

    def mark_as_login_required(self, video):
        self._lock.acquire()
        self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_LOGIN_REQUIRED)
        qe = self.get_qe_by_video_id(video.video_id)
        self._list.remove(qe)
        self._lock.release()

    def mark_as_referenced(self, video):
        self._lock.acquire()
        self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_REFERENCED)
        qe = self.get_qe_by_video_id(video.video_id)
        self._list.remove(qe)
        self._lock.release()

    def enqueue_again(self, video):
        self._lock.acquire()

        qe = self.get_qe_by_video_id(video.video_id)
        qe.is_available = True

        self._list.remove(qe)
        if qe.trials_remaining > 0:
            self._list.append(qe)

        self._lock.release()

    def get_qe_by_video_id(self, video_id):
        match_list = list(filter(lambda qe: qe.video.video_id == video_id, self._list))
        return match_list[0] if len(match_list) > 0 else None
