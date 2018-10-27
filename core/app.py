import logging
from abc import ABCMeta, abstractmethod

from core import config
from core.cyclic_queue import CyclicQueue
from core.download_thread import DownloadThread
from core.indexer.dynamodb import DynamoDbIndexer
from core.model.factory import Factory
from core.repeated_timer import RepeatedTimer
from core.storage.google_drive import GoogleDrive

logger = logging.getLogger(__name__)
k_REQUEST_FOLDER = 'requests'


class App(metaclass=ABCMeta):
    def __init__(self):
        self.queue = CyclicQueue(indexer=self.create_indexer())
        self.storage = self.get_storage()
        self.threads = self.create_thread_pool()

    def create_thread_pool(self):
        threads = []
        for i in range(config.global_instance['thread_count']):
            threads.append(self.create_thread())
        return threads

    def get_storage(self):
        if 'google_drive_folder_id' in config.global_instance:
            storage = GoogleDrive(config=config.global_instance)
            logger.info('Initialized storage object with config')
            return storage
        storage = GoogleDrive()
        logger.info('Initialized storage object with default settings')
        return storage

    @abstractmethod
    def create_thread(self):
        pass

    @abstractmethod
    def create_indexer(self):
        pass


class AppSingleMode(App):
    def __init__(self, url):
        App.__init__(self)
        self._process(url)

    def create_thread(self):
        return DownloadThread(queue=self.queue, storage=self.storage)

    def _process(self, url):
        f = Factory(url=url, logger=logger)
        vids = f.get_videos(min_mylist=config.global_instance['minimum_mylist'] if f.type != Factory.k_MYLIST else 0)
        self.queue.enqueue(vids)
        for thread in self.threads:
            thread.start()
        self.wait_and_quit()

    def wait_and_quit(self):
        for thread in self.threads:
            thread.join()
        self.queue.replenish_timer.stop()

    def create_indexer(self):
        return None


class AppDaemonMode(App):
    def __init__(self):
        App.__init__(self)
        for thread in self.threads:
            thread.start()
        self.daily_trend_timer = RepeatedTimer(43200, self.explore_daily_trending_videos)  # every 12 hours

    def create_thread(self):
        return DownloadThread(queue=self.queue, storage=self.storage, is_daemon=True, is_crawl=True)

    def explore_daily_trending_videos(self):
        logger.info('Enqueuing daily trends...')
        url = 'https://www.nicovideo.jp/ranking/fav/daily/sing'
        vids = Factory(url=url, logger=logger).get_videos(min_mylist=config.global_instance['minimum_mylist'])
        self.queue.enqueue(vids)

    def create_indexer(self):
        aws_required_fields = ['aws_region', 'aws_access_key_id', 'aws_secret_access_key']
        for field in aws_required_fields:
            if field not in config.global_instance:
                return None
        return DynamoDbIndexer(config=config.global_instance)
