import os

from youtube_dl import YoutubeDL
import logging

from core import global_config

log = logging.getLogger(__name__)
k_DOWNLOADS_FOLDER_PATH = 'downloads'


class CustomYoutubeDL(YoutubeDL):
    def __init__(self, video):
        YoutubeDL.__init__(self, params=get_ydl_options(video.requires_creds))
        self.video = video

    def download(self):
        try:
            return YoutubeDL.download(self, [self.video.url])
        except Exception as e:
            if 'unable to obtain file audio codec with ffprobe' in str(e):
                return 0
            else:
                raise

    @property
    def filename(self):
        files = os.listdir(k_DOWNLOADS_FOLDER_PATH)
        filtered_list = list(filter(lambda f: self.video.video_id in f, files))
        if filtered_list and len(filtered_list) == 1:
            return filtered_list[0]
        return None

    @property
    def path(self):
        if self.filename:
            return '{}/{}'.format(k_DOWNLOADS_FOLDER_PATH, self.filename)
        else:
            return None

    def remove_local_file(self):
        path = self.path
        if path:
            os.remove(path)


def get_ydl_options(requires_creds=False):
    options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '{}/%(upload_date)-s%(title)s-%(id)s.%(ext)s'.format(k_DOWNLOADS_FOLDER_PATH),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': global_config.instance['convert_to'],
            'preferredquality': '320',
        }],
        'logger': SilentLogger()
    }
    if requires_creds:
        options['username'] = global_config.instance['nico_username']
        options['password'] = global_config.instance['nico_password']
    return options


class SilentLogger(object):
    def debug(self, msg):
        log.debug(msg)

    def warning(self, msg):
        log.debug(msg)

    def error(self, msg):
        log.debug(msg)
