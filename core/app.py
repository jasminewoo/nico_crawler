import json
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
from indexer.dynamodb import DynamoDbIndexer
from indexer.local import LocalIndexer
from storage.google_drive import GoogleDrive

log = logging.getLogger(__name__)
k_REQUEST_FOLDER = './requests'
k_SECRET_CONFIG_FILENAME = 'config_secret.json'


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
        self.queue.timer.stop()


class AppDaemonMode(App):
    def __init__(self):
        App.__init__(self)
        for thread in self.threads:
            thread.start()
        self.detection_timer = RepeatedTimer(self.detect_new_requests)

    def create_thread(self):
        return DownloadThread(queue=self.queue, storage=self.storage, is_daemon=True, is_crawl=True)

    def detect_new_requests(self):
        if not os.path.exists(k_REQUEST_FOLDER):
            return
        for item in os.listdir(k_REQUEST_FOLDER):
            path = '{}/{}'.format(k_REQUEST_FOLDER, item)
            if not os.path.isfile(path):
                continue
            with open(path, 'r') as fp:
                for line in fp.readlines():
                    self.queue.enqueue(url=line)
            os.remove(path)


def _get_storage():
    if os.path.exists(k_SECRET_CONFIG_FILENAME):
        with open(k_SECRET_CONFIG_FILENAME, 'r') as fp:
            config = json.load(fp)
            if 'google_drive_folder_id' in config:
                storage = GoogleDrive(config=config)
                log.info('Initialized storage object with config')
                return storage
    storage = GoogleDrive()
    log.info('Initialized storage object with default settings')
    return storage


def _get_indexer():
    indexer = LocalIndexer()
    aws_required_fields = ['aws_region', 'aws_access_key_id', 'aws_secret_access_key']
    if os.path.exists(k_SECRET_CONFIG_FILENAME):
        with open(k_SECRET_CONFIG_FILENAME, 'r') as fp:
            config = json.load(fp)
            for field in aws_required_fields:
                if field not in config:
                    return indexer
            return DynamoDbIndexer(config=config)
    return indexer
