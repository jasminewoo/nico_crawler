from abc import ABCMeta, abstractmethod


class Indexer(metaclass=ABCMeta):
    k_STATUS_DONE = 'done'
    k_STATUS_PENDING = 'pending'
    k_STATUS_NOT_FOUND = 'not_found'
    k_STATUS_REJECTED = 'rejected'
    k_STATUS_ERRORED = 'errored'
    k_STATUS_REFERENCED = 'referenced'
    k_STATUS_LOGIN_REQUIRED = 'login_required'

    def __init__(self, config=None):
        self.config = config

    @abstractmethod
    def get_status(self, video_id):
        pass

    @abstractmethod
    def set_status(self, video_id, status):
        pass

    @abstractmethod
    def get_pending_video_ids(self, max_id_count=None):
        pass

    def exists(self, video_id):
        status = self.get_status(video_id=video_id)
        return status != self.k_STATUS_NOT_FOUND
