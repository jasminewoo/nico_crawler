import logging

from MyList import MyList
from Search import Search
from Video import Video
from cyclic_queue import CyclicQueue

log = logging.getLogger(__name__)


class App:
    def __init__(self):
        self.queue = CyclicQueue()
        # TODO create thread pool
        # TODO: wait for all threads to .join()

    def process(self, url):
        if 'mylist' in url:
            videos = MyList(url=url).videos
        elif 'search' in url:
            videos = Search(url=url).videos
        else:
            videos = [Video(url=url)]

        for video in videos:
            self.queue.enqueue(video)
