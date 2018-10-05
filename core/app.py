import logging
import os
from abc import ABCMeta, abstractmethod

from core import global_config
from core.cyclic_queue import CyclicQueue
from core.download_thread import DownloadThread
from core.mylist import MyList
from core.repeated_timer import RepeatedTimer
from core.search import Search
from core.video import Video

log = logging.getLogger(__name__)


class App(metaclass=ABCMeta):
    def __init__(self):
        self.queue = CyclicQueue()
        self.threads = self.create_thread_pool()

    def create_thread_pool(self):
        threads = []
        for i in range(global_config.instance['thread_count']):
            threads.append(self.create_thread())
        return threads

    @abstractmethod
    def create_thread(self):
        pass

    def _enqueue_url(self, url):
        if 'mylist' in url:
            videos = MyList(url=url).videos
        elif 'search' in url:
            videos = Search(url=url).videos
        else:
            videos = [Video(url=url)]

        for video in videos:
            self.queue.enqueue(video)


class AppSingleMode(App):
    def __init__(self, url):
        App.__init__(self)
        self._process(url)

    def create_thread(self):
        return DownloadThread(queue=self.queue)

    def _process(self, url):
        self._enqueue_url(url)
        for thread in self.threads:
            thread.start()
        self.wait_and_quit()

    def wait_and_quit(self):
        for thread in self.threads:
            thread.join()
        self.queue.timer.stop()


class AppDaemonMode(App):
    def __init__(self):
        App.__init__(self)
        for thread in self.threads:
            thread.start()
        self.detection_timer = RepeatedTimer(self.detect_new_requests)

    def create_thread(self):
        return DownloadThread(queue=self.queue, is_daemon=True)

    def detect_new_requests(self):
        if not os.path.exists('requests'):
            return
        for item in os.listdir('requests'):
            if not os.path.isfile(item):
                continue
            with open(item, 'r') as fp:
                for line in fp.readlines():
                    self._enqueue_url(line)
            os.remove(item)
