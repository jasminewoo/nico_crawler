from abc import ABCMeta, abstractmethod


class Indexer(metaclass=ABCMeta):
    k_STATUS_DONE = 'done'
    k_STATUS_NOT_FOUND = 'not_found'

    def __init__(self, config=None):
        self.config = config

    @abstractmethod
    def get_status(self, video_id):
        pass

    @abstractmethod
    def set_status(self, video_id, status):
        pass

    def is_done(self, video_id):
        status = self.get_status(video_id=video_id)
        return status == self.k_STATUS_DONE
