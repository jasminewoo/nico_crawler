import logging
from multiprocessing import Lock

from core import global_config
from core.video import Video
from indexer.indexer_service import Indexer

log = logging.getLogger(__name__)


class QueueElement:
    def __init__(self, video):
        self.video = video
        self.is_available = True
        self.trials_remaining = global_config.instance['max_retry']
        self.is_done = False


class CyclicQueue:
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

    def enqueue(self, video):
        self._lock.acquire()

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
            if qe.is_available and qe.trials_remaining > 0 and not qe.is_done:
                qe.is_available = False
                to_return = qe.video
                break

        self._lock.release()

        return to_return

    def mark_as_done(self, video):
        self._lock.acquire()

        for qe in self._list:
            if qe.video.video_id == video.video_id:
                self.indexer.set_status(video_id=video.video_id, status=Indexer.k_STATUS_DONE)
                qe.is_done = True
                break

        self._lock.release()

    def enqueue_again(self, video):
        self._lock.acquire()

        match_list = list(filter(lambda qe: qe.video.video_id == video.video_id, self._list))
        if len(match_list) > 0:
            qe = match_list[0]
            self._list.remove(qe)
            qe.is_available = True
            qe.trials_remaining -= 1
            self._list.append(qe)
        else:
            log.debug('{} was not found in the queue'.format(video))

        self._lock.release()
