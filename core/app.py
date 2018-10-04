import logging
import random
import time

import global_config
from core.cyclic_queue import CyclicQueue
from core.download_thread import DownloadThread
from core.mylist import MyList
from core.search import Search
from core.video import Video

log = logging.getLogger(__name__)


class App:
    def __init__(self):
        self.queue = CyclicQueue()

    def process(self, url):
        if 'mylist' in url:
            videos = MyList(url=url).videos
        elif 'search' in url:
            videos = Search(url=url).videos
        else:
            videos = [Video(url=url)]

        for video in videos:
            self.queue.enqueue(video)

        ct = global_config.instance['concurrent_threads']
        threads = []
        for i in range(ct):
            t = DownloadThread(queue=self.queue, thread_number=i)
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()

        # At this point there is nothing left on the queue
        self.queue.stop_timer()
