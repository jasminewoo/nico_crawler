from indexer.indexer_service import Indexer


class LocalMemoryIndexer(Indexer):
    def __init__(self, config=None):
        Indexer.__init__(self, config=config)
        self.map = {}

    def get_status(self, video_id):
        return self.map[video_id] if video_id in self.map else self.k_STATUS_NOT_FOUND

    def set_status(self, video_id, status):
        self.map[video_id] = status
