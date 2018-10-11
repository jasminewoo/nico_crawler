from abc import ABCMeta, abstractmethod


class Indexer(metaclass=ABCMeta):
    k_STATUS_DONE = 'done'
    k_STATUS_PENDING = 'pending'
    k_STATUS_NOT_FOUND = 'not_found'
    k_STATUS_REJECTED = 'rejected'
    k_STATUS_ERRORED = 'errored'

    def __init__(self, config=None):
        self.config = config

    @abstractmethod
    def get_status(self, video_id):
        pass

    @abstractmethod
    def set_status(self, video_id, status):
        pass

    @abstractmethod
    def get_pending_video_ids(self):
        pass

    @abstractmethod
    def set_trials_remaining(self, video_id, trials_remaining):
        pass

    def exists(self, video_id):
        status = self.get_status(video_id=video_id)
        return status != self.k_STATUS_NOT_FOUND
