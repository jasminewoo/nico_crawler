from multiprocessing import Lock

k_DEFAULT_DISK_LOCATION = 'queue.csv'


class CyclicQueue:
    def __init__(self):
        self.lock = Lock()
        self.list = []

    def _write(self):
        pass
