import logging
import random
import time
from threading import Thread

log = logging.getLogger(__name__)


class DownloadThread(Thread):
    def __init__(self, queue, thread_number=-1):
        Thread.__init__(self)
        self.queue = queue
        self.thread_number = thread_number

    def run(self):
        while True:
            video = self.queue.peek_and_reserve()
            if video:
                log.debug('Starting to process {}'.format(video))
                success = _get_dummy_result()
                if success:
                    self.queue.mark_as_done(video)
                    log.info('Finished: {}'.format(video))
                else:
                    self.queue.enqueue_again(video)
                    log.info('Failed:   {}'.format(video))
            else:
                log.debug('This thread is out of work. Existing now...')
                break


def _get_dummy_result():
    time.sleep(1)
    return random.randint(0,1) == 1
