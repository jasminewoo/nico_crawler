from __future__ import unicode_literals
import youtube_dl
import logging

from core import global_config

logging.getLogger('youtube_dl').setLevel('CRITICAL')
log = logging.getLogger(__name__)


class Video:
    def __init__(self, video_id=None, url=None, title=None):
        if (1 if video_id else 0) + (1 if url else 0) != 1:
            raise AssertionError('Need one of video_id and url')

        if url:
            self.video_id = url.split('/')[-1]
        if video_id:
            self.video_id = video_id
        self.title = title

    def __str__(self):
        return '{} {}'.format(self.title, self.video_id) if self.title else self.video_id

    @property
    def url(self):
        return 'http://www.nicovideo.jp/watch/' + self.video_id

    def download(self):
        if not self.video_id:
            raise AssertionError('self.video_id must be provided')

        is_successful = False

        ydl = youtube_dl.YoutubeDL(get_ydl_options())
        ret_code = ydl.download([self.url])

        if ret_code == 0:
            convert_to = global_config.instance['convert_to']
            # TODO: convert
            is_successful = True

        return is_successful


class SilentLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        log.error(msg)


def get_ydl_options():
    return {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '320',
        }],
        'logger': SilentLogger(),
        'progress_hooks': [my_hook],
    }


def my_hook(d):
    if d['status'] == 'finished':
        log.debug('Done downloading, now converting ...')
