import logging
import os
from multiprocessing import Lock

from core import global_config
from core.video import Video
from core.repeated_timer import RepeatedTimer

k_DEFAULT_DISK_LOCATION = 'queue.txt'

log = logging.getLogger(__name__)


class QueueElement:
    def __init__(self, video):
        self.video = video
        self.is_available = True
        self.trials_remaining = global_config.instance['max_retry']
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
                log.debug('Already in the queue: {}'.format(video))
                exists = True
                break

        if not exists:
            self._list.append(QueueElement(video))

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
            qe_to_enqueue_again.trials_remaining -= 1
            self._list.append(qe_to_enqueue_again)
        else:
            log.debug('{} was not found in the queue'.format(video))

        self._lock.release()

    def load_from_previous_session(self):
        if os.path.exists(k_DEFAULT_DISK_LOCATION):
            with open(k_DEFAULT_DISK_LOCATION, 'r') as fp:
                for video_id in fp.readlines():
                    if video_id == '':
                        continue
                    video = Video(video_id=video_id.strip('\n').strip())
                    qe = QueueElement(video=video)
                    self._list.append(qe)

    def _write(self):
        self._lock.acquire()
        if os.path.exists(k_DEFAULT_DISK_LOCATION):
            os.rename(k_DEFAULT_DISK_LOCATION, k_DEFAULT_DISK_LOCATION + '.bak')
        with open(k_DEFAULT_DISK_LOCATION, 'w') as fp:
            for qe in self._list:
                if not qe.is_done:
                    fp.write(qe.video.video_id + '\n')
        self._lock.release()
