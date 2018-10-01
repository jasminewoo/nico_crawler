import logging

from nicotools.download import Video as NicoToolsVideo

import global_config

log = logging.getLogger(__name__)


class Video:
    def __init__(self, url=None, info=None):
        self.title = None
        if info:
            self._js = info
            self.video_id = info['video_id']
            self.title = info['title']
            self.is_available = info['deleted'] == '0'
        else:
            self.video_id = url.split('/')[-1]

    def __str__(self):
        return '{} {}'.format(self.title, self.video_id) if self.title else self.video_id

    def download(self):
        if not self.is_available:
            log.info('Skip: the video was deleted {}'.format(self))
        if not self.video_id:
            raise AssertionError('self.video_id must be provided')

        mail = global_config.instance['email']
        password = global_config.instance['password']

        video_ids = [self.video_id]
        dir_path = global_config.instance['download_location']

        NicoToolsVideo(video_ids, save_dir=dir_path, mail=mail, password=password).start()
