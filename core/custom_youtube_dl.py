import logging
import os
from urllib.error import URLError

from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError, DownloadError

from core import global_config

logging.getLogger('niconico').setLevel('CRITICAL')
logging.getLogger('youtube_dl').setLevel('CRITICAL')

k_DOWNLOADS_FOLDER_PATH = 'downloads'


class CustomYoutubeDL(YoutubeDL):
    def __init__(self, video, logger=None):
        creds = video.requires_creds_to_download
        params = get_ydl_options(title=video.title, requires_creds=creds, logger=logger)
        YoutubeDL.__init__(self, params=params)
        self.video = video

    def download(self):
        return YoutubeDL.download(self, [self.video.url])

    @property
    def filename(self):
        if os.path.exists(k_DOWNLOADS_FOLDER_PATH):
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
        os.remove(self.path)


def download(video, logger, storage):
    ydl = CustomYoutubeDL(video, logger)
    try:
        if ydl.download() != 0:
            raise RuntimeError('Download failed')
        if storage:
            storage.upload_file(ydl.filename, ydl.path)
    except (URLError, ExtractorError, DownloadError, MemoryError) as e:
        if 'Niconico videos now require logging in' in str(e):
            raise LogInError
        else:
            logger.debug(e)
            raise RetriableError
    finally:
        if storage and ydl.path:
            ydl.remove_local_file()


def sanitize_title(video_title):
    video_title = video_title.replace('/', ' ')
    while '  ' in video_title:
        video_title = video_title.replace('  ', ' ')
    return video_title


def get_ydl_options(title=None, requires_creds=False, logger=None):
    title_format = title if title else '%(title)s'
    options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '{}/%(upload_date)s-{}-%(id)s.%(ext)s'.format(k_DOWNLOADS_FOLDER_PATH, title_format),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': global_config.instance['convert_to'],
            'preferredquality': '320',
        }],
        'noprogress': True
    }

    if logger:
        options['logger'] = SilentLogger(logger=logger)

    if requires_creds:
        options['username'] = global_config.instance['nico_username']
        options['password'] = global_config.instance['nico_password']

    return options


class SilentLogger:
    def __init__(self, logger):
        self.logger = logger

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.debug(msg)

    def error(self, msg):
        self.logger.debug(msg)


class RetriableError(Exception):
    pass


class LogInError(Exception):
    pass
