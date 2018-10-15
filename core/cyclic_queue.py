import logging
from datetime import datetime, timedelta
from multiprocessing import Lock

from core import global_config
from core.nico_object_factory import NicoObjectFactory
from core.repeated_timer import RepeatedTimer
from core.video import Video
from indexer.indexer_service import Indexer

log = logging.getLogger(__name__)

k_MAX_QUEUE_SIZE = 1000


class QueueElement:
    def __init__(self, video):
        self.video = video
        self.is_available = True
        self.trials_remaining = global_config.instance['max_retry']
        self.next_trial_timestamp = datetime.utcnow()

    def __str__(self):
        return self.video.video_id


class CyclicQueue:
    k_RE_ENQUEUE_MODE_SEND_TO_BACK = 'send_to_back'
    k_RE_ENQUEUE_MODE_KEEP_POSITION = 'keep_position'

    def __init__(self, indexer=None):
        self._lock = Lock()
        self._list = []
        self.indexer = indexer
        self.replenish_timer = RepeatedTimer(30, self.replenish)
        self.load_from_previous_session()

    def load_from_previous_session(self):
        log.info('Loading previous session from indexer...')
        pending_video_ids = self.indexer.get_pending_video_ids(max_id_count=k_MAX_QUEUE_SIZE)
        log.info('len(pending_video_ids) = {}'.format(len(pending_video_ids)))
        for video_id in pending_video_ids:
            video = Video(video_id=video_id)
            qe = QueueElement(video=video)
            self._list.append(qe)

    def replenish(self):
        if len(self._list) > k_MAX_QUEUE_SIZE // 10:
            return

        new_video_ids = self.indexer.get_pending_video_ids(max_id_count=k_MAX_QUEUE_SIZE)
        self._lock.acquire()
        existing_video_ids = [str(qe) for qe in self._list]
        for new_video_id in new_video_ids:
            if new_video_id not in existing_video_ids:
                video = Video(video_id=new_video_id)
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
            can_try = qe.trials_remaining > 0 and qe.next_trial_timestamp < datetime.utcnow()
            if qe.is_available and can_try:
                qe.is_available = False
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

    def enqueue_again(self, video, mode=k_RE_ENQUEUE_MODE_SEND_TO_BACK):
        self._lock.acquire()

        qe = self.get_qe_by_video_id(video.video_id)
        qe.is_available = True
        qe.trials_remaining -= 1

        if qe.trials_remaining > 0:
            if mode == self.k_RE_ENQUEUE_MODE_SEND_TO_BACK:
                qe.next_trial_timestamp += timedelta(seconds=global_config.instance['retry_interval_in_seconds'])
                self._list.remove(qe)
                self._list.append(qe)
        else:
            self.indexer.set_status(video_id=qe.video.video_id, status=Indexer.k_STATUS_ERRORED)
            self._list.remove(qe)

        self._lock.release()

    def get_qe_by_video_id(self, video_id):
        match_list = list(filter(lambda qe: qe.video.video_id == video_id, self._list))
        return match_list[0] if len(match_list) > 0 else None
