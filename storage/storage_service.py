from abc import ABCMeta, abstractmethod


class StorageService(metaclass=ABCMeta):
    def __init__(self, config=None):
        self.config = config

    @abstractmethod
    def upload_file(self, name, path):
        pass

    @abstractmethod
    def upload_bytes(self, name, data):
        pass

    @abstractmethod
    def update_with_file(self, key, path):
        pass

    @abstractmethod
    def update_with_bytes(self, key, data):
        pass

    @abstractmethod
    def download_as_bytes(self, key):
        pass

    @abstractmethod
    def download_as_file(self, key, dst_path):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    @abstractmethod
    def exists(self, key):
        pass
