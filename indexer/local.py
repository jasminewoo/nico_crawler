from multiprocessing import Lock

from indexer.indexer_service import Indexer

k_DEFAULT_DISK_LOCATION = 'queue.txt'


class LocalIndexer(Indexer):
    def __init__(self, config=None):
        Indexer.__init__(self, config=config)
        self.map = {}
        self.load_from_disk()
        # self._timer = RepeatedTimer(self._write)
        self._lock = Lock()

    def load_from_disk(self):
        # if os.path.exists(k_DEFAULT_DISK_LOCATION):
        #     with open(k_DEFAULT_DISK_LOCATION, 'r') as fp:
        #         for line in fp.readlines():
        #             if line == '':
        #                 continue
        #             line_split = line.split(',')
        #             video_id = line_split[0].strip('\n').strip()
        #             status = line_split[1] if len(line_split) > 1 else self.k_STATUS_PENDING
        #             self.map[video_id] = status
        pass

    def get_pending_video_ids(self, max_id_count=None):
        l = list(filter(lambda video_id: map['video_id'] == self.k_STATUS_PENDING, self.map))
        if max_id_count and len(l) > max_id_count:
            l = l[:max_id_count]
        return l

    def get_status(self, video_id):
        return self.map[video_id] if video_id in self.map else self.k_STATUS_NOT_FOUND

    def set_trials_remaining(self, video_id, trials_remaining):
        pass

    def set_status(self, video_id, status):
        self._lock.acquire()
        # self.map[video_id] = status
        # with open(k_DEFAULT_DISK_LOCATION, 'w') as fp:
        #     for video_id in self.map:
        #         if not qe.is_done:
        #             fp.write(qe.video.video_id + '\n')
        self._lock.release()

    def _write(self):
        self._lock.acquire()
        # if os.path.exists(k_DEFAULT_DISK_LOCATION):
        #     os.rename(k_DEFAULT_DISK_LOCATION, k_DEFAULT_DISK_LOCATION + '.bak')
        # with open(k_DEFAULT_DISK_LOCATION, 'w') as fp:
        #     for qe in self._list:
        #         if not qe.is_done:
        #             fp.write(qe.video.video_id + '\n')
        self._lock.release()
