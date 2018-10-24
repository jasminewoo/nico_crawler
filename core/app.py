import logging
import os
from abc import ABCMeta, abstractmethod

from core import global_config
from core.cyclic_queue import CyclicQueue
from core.download_thread import DownloadThread
from core.repeated_timer import RepeatedTimer
from indexer.dynamodb import DynamoDbIndexer
from storage.google_drive import GoogleDrive

log = logging.getLogger(__name__)
k_REQUEST_FOLDER = 'requests'


class App(metaclass=ABCMeta):
    def __init__(self):
        self.queue = CyclicQueue(indexer=_get_indexer())
        self.storage = _get_storage()
        self.threads = self.create_thread_pool()

    def create_thread_pool(self):
        threads = []
        for i in range(global_config.instance['thread_count']):
            threads.append(self.create_thread())
        return threads

    @abstractmethod
    def create_thread(self):
        pass


class AppSingleMode(App):
    def __init__(self, url):
        App.__init__(self)
        self._process(url)

    def create_thread(self):
        return DownloadThread(queue=self.queue, storage=self.storage)

    def _process(self, url):
        self.queue.enqueue(url=url)
        for thread in self.threads:
            thread.start()
        self.wait_and_quit()

    def wait_and_quit(self):
        for thread in self.threads:
            thread.join()
        self.queue.replenish_timer.stop()


class AppDaemonMode(App):
    def __init__(self):
        App.__init__(self)
        for thread in self.threads:
            thread.start()
        self.daily_trend_timer = RepeatedTimer(43200, self.explore_daily_trending_videos)  # every 12 hours

    def create_thread(self):
        return DownloadThread(queue=self.queue, storage=self.storage, is_daemon=True, is_crawl=True)

    def explore_daily_trending_videos(self):
        log.info('Enqueuing daily trends...')
        self.queue.enqueue(url='https://www.nicovideo.jp/ranking/fav/daily/sing')


def _get_storage():
    if 'google_drive_folder_id' in global_config.instance:
        storage = GoogleDrive(config=global_config.instance)
        log.info('Initialized storage object with config')
        return storage
    storage = GoogleDrive()
    log.info('Initialized storage object with default settings')
    return storage


def _get_indexer():
    aws_required_fields = ['aws_region', 'aws_access_key_id', 'aws_secret_access_key']
    for field in aws_required_fields:
        if field not in global_config.instance:
            raise AssertionError('AWS credentials must be provided')
    return DynamoDbIndexer(config=global_config.instance)
