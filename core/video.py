import logging

import youtube_dl

import global_config

log = logging.getLogger(__name__)


class Video:
    def __init__(self, video_id=None, url=None, info=None):
        self.title = None
        self.is_available = True
        if url:
            self.video_id = url.split('/')[-1]
        if info:
            self.video_id = info['video_id']
            self.title = info['title']
            self.is_available = info['deleted'] == '0'
        if video_id:
            self.video_id = video_id

    def __str__(self):
        return '{} {}'.format(self.title, self.video_id) if self.title else self.video_id

    @property
    def url(self):
        pass

    def download(self):
        if not self.video_id:
            raise AssertionError('self.video_id must be provided')

        is_successful = False

        ydl = youtube_dl.YoutubeDL(params=get_params())
        ret_code = ydl.download([self.url])

        if ret_code == 0:
            convert_to = global_config.instance['convert_to']
            # TODO: convert
            is_successful = True

        return is_successful


def get_params():
    # TODO: enter things here
    return []
