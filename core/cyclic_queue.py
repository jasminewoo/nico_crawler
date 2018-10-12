import logging
from datetime import datetime, timedelta
from multiprocessing import Lock

from core import global_config
from core.nico_object_factory import NicoObjectFactory
from core.video import Video
from indexer.indexer_service import Indexer

log = logging.getLogger(__name__)


class QueueElement:
    def __init__(self, video):
        self.video = video
        self.is_available = True
        self.trials_remaining = global_config.instance['max_retry']
        self.is_done = False
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
        self.load_from_previous_session()

    def load_from_previous_session(self):
        pending_video_ids = self.indexer.get_pending_video_ids()
        for video_id in pending_video_ids:
            video = Video(video_id=video_id)
            qe = QueueElement(video=video)
            self._list.append(qe)

    def enqueue(self, video=None, url=None):
        if (1 if video else 0) + (1 if url else 0) != 1:
            AssertionError('Only one parameter allowed')

        if url:
            videos = NicoObjectFactory(url=url).get_videos()
        else:
            videos = [video]

        self._lock.acquire()
        for video in videos:
            exists = self.indexer.exists(video_id=video.video_id)
            if not exists:
                self._list.append(QueueElement(video))
                self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_PENDING)
                log.info('Enqueued:  {}'.format(video.video_id))
            else:
                log.info('Duplicate: {}'.format(video.video_id))
        self._lock.release()

    def peek_and_reserve(self):
        self._lock.acquire()

        to_return = None
        for qe in self._list:
            is_free = qe.is_available and not qe.is_done
            can_try = qe.trials_remaining > 0 and qe.next_trial_timestamp < datetime.utcnow()
            if is_free and can_try:
                qe.is_available = False
                to_return = qe.video
                break

        self._lock.release()

        return to_return

    def mark_as_done(self, video):
        self._lock.acquire()
        qe = self.get_qe_by_video_id(video.video_id)
        self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_DONE)
        qe.is_done = True
        self._lock.release()

    def mark_as_login_required(self, video):
        self._lock.acquire()
        self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_LOGIN_REQUIRED)
        self._lock.release()

    def mark_as_referenced(self, video):
        self._lock.acquire()
        qe = self.get_qe_by_video_id(video.video_id)
        qe.trials_remaining = 0
        self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_REFERENCED)
        self._lock.release()

    def enqueue_again(self, video, mode=k_RE_ENQUEUE_MODE_SEND_TO_BACK):
        self._lock.acquire()

        qe = self.get_qe_by_video_id(video.video_id)

        qe.is_available = True
        qe.trials_remaining -= 1
        if qe.trials_remaining == 0:
            self.indexer.set_status(video_id=qe.video.video_id, status=Indexer.k_STATUS_ERRORED)

        if mode == self.k_RE_ENQUEUE_MODE_SEND_TO_BACK:
            qe.next_trial_timestamp += timedelta(seconds=global_config.instance['retry_interval_in_seconds'])
            self._list.remove(qe)
            self._list.append(qe)

        self._lock.release()

    def get_qe_by_video_id(self, video_id):
        match_list = list(filter(lambda qe: qe.video.video_id == video_id, self._list))
        return match_list[0] if len(match_list) > 0 else None
