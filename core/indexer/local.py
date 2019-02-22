import os

from core.indexer.indexer_service import Indexer
from core.utils.path_utils import get_root_prefix

k_FILENAME = 'local_indexer'


class LocalIndexer(Indexer):
    def __init__(self, config=None):
        Indexer.__init__(self, config)
        self.filename = k_FILENAME
        if config and 'filename' in config:
            self.filename = config['filename']

    def _get_fp(self, filename=None, mode='r'):
        if not filename:
            filename = self.filename
        path = get_root_prefix() + filename
        if not os.path.exists(path):
            open(path, 'a').close()
        return open(path, mode)

    def get_status(self, video_id):
        with self._get_fp() as fp:
            for line in fp:
                if line.startswith(video_id):
                    return line.split(',')[1].strip('\n')
        return self.k_STATUS_NOT_FOUND

    def set_status(self, video_id, status):
        new_filename = 'tmp' + self.filename

        found_id = False
        with self._get_fp() as fp:
            with self._get_fp(new_filename, 'w') as fp_new:
                for line in fp:
                    if line == '':
                        continue
                    s = line.split(',')
                    if s[0] == video_id:
                        found_id = True
                        line = s[0] + ',' + status
                    fp_new.write(line)
                if not found_id:
                    fp_new.write('{},{}\n'.format(video_id, status))
        prefix = get_root_prefix()
        os.rename(prefix + new_filename, prefix + self.filename)

    def get_video_ids_by_status(self, status, max_result_set_size=None):
        ids = []
        with self._get_fp() as fp:
            for line in fp:
                line = line.split(',')
                if line[1] == status:
                    ids.append(line[0])
                    if max_result_set_size and len(ids) == max_result_set_size:
                        break
        return ids

    def get_all_video_ids_as_set(self):
        ids = set()
        with self._get_fp() as fp:
            for line in fp:
                ids.add(line.split(',')[0])
        return ids
