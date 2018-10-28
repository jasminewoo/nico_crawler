import logging
from multiprocessing import Lock

from core.repeated_timer import RepeatedTimer
from core.model.video import Video
from core.indexer.indexer_service import Indexer

k_MAX_QUEUE_SIZE = 300
k_MAX_RETRY = 3

default_logger = logging.getLogger(__name__)


class QueueElement:
    def __init__(self, video):
        self.video = video
        self.is_available = True
        self.trials_remaining = 1 + k_MAX_RETRY

    def __str__(self):
        return self.video.video_id


class CyclicQueue:
    def __init__(self, indexer):
        self._lock = Lock()
        self._list = []
        self.indexer = indexer
        self.cached_indexer = self.indexer.get_all_video_ids_as_set()
        self.replenish_timer = RepeatedTimer(30, self.replenish)

    def replenish(self):
        if len(self._list) > k_MAX_QUEUE_SIZE // 10:
            return

        default_logger.debug('len(queue)={}'.format(len(self._list)))

        pending = self.indexer.get_video_ids_by_status(Indexer.k_STATUS_PENDING,
                                                       max_result_set_size=k_MAX_QUEUE_SIZE // 2)
        login_failed = self.indexer.get_video_ids_by_status(Indexer.k_STATUS_LOGIN_REQUIRED,
                                                            max_result_set_size=k_MAX_QUEUE_SIZE // 10)

        self._append_all(pending)
        self._append_all(login_failed)

    def _append_all(self, video_ids):
        default_logger.debug('len(video_ids)={}'.format(len(video_ids)))
        self._lock.acquire()
        existing_video_ids = {}
        for qe in self._list:
            existing_video_ids[str(qe)] = None
        for new_video_id in video_ids:
            if new_video_id not in existing_video_ids:
                video = Video(video_id=new_video_id)
                qe = QueueElement(video=video)
                self._list.append(qe)
        self._lock.release()

    def enqueue(self, videos):
        results = {'enqueued': 0, 'skipped': 0}
        self._lock.acquire()
        for video in videos:
            exists = video.video_id in self.cached_indexer or self.indexer.exists(video.video_id)
            if not exists:
                if len(self._list) <= k_MAX_QUEUE_SIZE:
                    self._list.append(QueueElement(video))
                self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_PENDING)
                self.cached_indexer.add(video.video_id)
                results['enqueued'] = results['enqueued'] + 1
            else:
                results['skipped'] = results['skipped'] + 1
        self._lock.release()
        return results

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
