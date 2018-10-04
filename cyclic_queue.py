import logging
import os
from multiprocessing import Lock

from Video import Video
from repeated_timer import RepeatedTimer

k_DEFAULT_DISK_LOCATION = 'queue.txt'

log = logging.getLogger(__name__)


class QueueElement:
    def __init__(self, video):
        self.video = video
        self.is_available = True
        self.is_done = False


class CyclicQueue:
    def __init__(self):
        self._lock = Lock()
        self._list = []
        self.load_from_previous_session()
        self.timer = RepeatedTimer(self._write)

    def enqueue(self, video):
        self._lock.acquire()

        exists = False
        for qe in self._list:
            if qe.video.video_id == video.video_id:
                log.debug('Trying to add {}, but it already exists in the queue'.format(video))
                exists = True
                break

        if not exists:
            self._list.append(QueueElement(video))

        self._lock.release()

    def peek_and_reserve(self):
        qe_to_return = None
        self._lock.acquire()
        for qe in self._list:
            if qe.is_available and not qe.is_done:
                qe.is_available = False
                qe_to_return = qe
        self._lock.release()
        return qe_to_return

    def mark_as_done(self, video):
        self._lock.acquire()

        found = False
        for qe in self._list:
            if qe.video.video_id == video.video_id:
                qe.is_done = True
                found = True
                break

        if not found:
            log.warning('{} was not found in the queue'.format(video))

        self._lock.release()

    def enqueue_again(self, video):
        self._lock.acquire()

        qe_to_enqueue_again = None
        for qe in self._list:
            if qe.video.video_id == video.video_id:
                qe_to_enqueue_again = qe
                break

        if qe_to_enqueue_again:
            self._list.remove(qe_to_enqueue_again)
            qe_to_enqueue_again.is_available = True
            self._list.append(qe_to_enqueue_again)
        else:
            log.warning('{} was not found in the queue'.format(video))

        self._lock.release()

    def load_from_previous_session(self):
        self._lock.acquire()
        if os.path.exists(k_DEFAULT_DISK_LOCATION):
            with open(k_DEFAULT_DISK_LOCATION, 'r') as fp:
                for video_id in fp.readlines():
                    video = Video(video_id=video_id)
                    qe = QueueElement(video=video)
                    self._list.append(qe)

        self._lock.release()

    def _write(self):
        self._lock.acquire()
        if os.path.exists(k_DEFAULT_DISK_LOCATION):
            os.rename(k_DEFAULT_DISK_LOCATION, k_DEFAULT_DISK_LOCATION + '.bak')
        with open(k_DEFAULT_DISK_LOCATION, 'w') as fp:
            for qe in self._list:
                fp.write(qe.video.video_id)
        self._lock.release()
