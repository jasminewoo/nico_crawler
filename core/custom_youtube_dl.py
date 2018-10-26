import base64
import logging
import os
import unicodedata
from urllib.error import URLError

from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError, DownloadError

from core import global_config

logging.getLogger('niconico').setLevel('CRITICAL')
logging.getLogger('youtube_dl').setLevel('CRITICAL')

k_DOWNLOADS_FOLDER_PATH = 'downloads'


class CustomYoutubeDL(YoutubeDL):
    def __init__(self, video, logger=None):
        params = get_ydl_options(title=video.title, logger=logger)
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
    video_title = unicodedata.normalize('NFKC', video_title)
    for key, value in global_config.instance['title_sanitization'].items():
        if key in video_title:
            video_title = video_title.replace(key, value)
    while '  ' in video_title:
        video_title = video_title.replace('  ', ' ')
    return video_title


def encode_title(video_title):
    return base64.urlsafe_b64encode(str.encode(video_title)).decode()


def decode_title(b64str):
    return base64.urlsafe_b64decode(b64str.encode()).decode()


def get_ydl_options(title=None, logger=None):
    title = sanitize_title(title) if title else '%(title)s'
    options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '{}/%(upload_date)s-{}-%(id)s.%(ext)s'.format(k_DOWNLOADS_FOLDER_PATH, title),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': global_config.instance['convert_to'] if 'convert_to' in global_config.instance else 'm4a',
            'preferredquality': '320',
        }],
        'noprogress': True
    }

    if logger:
        cl = logger if type(logger) is CustomLogger else CustomLogger(logger=logger)
        options['logger'] = cl
        options['progress_hooks']: [cl.hook]

    if 'nico_username' in global_config.instance and 'nico_password' in global_config.instance:
        options['username'] = global_config.instance['nico_username']
        options['password'] = global_config.instance['nico_password']

    return options


class CustomLogger:
    def __init__(self, logger):
        self.logger = logger
        self.history = []

    def debug(self, msg):
        self.log_with_history(self.logger.debug, msg)

    def warning(self, msg):
        self.log_with_history(self.logger.debug, msg)

    def error(self, msg):
        self.log_with_history(self.logger.debug, msg)

    def hook(self, d):
        if d['status'] == 'finished':
            self.log_with_history(self.logger.debug, 'Done downloading, now converting ...')
        else:
            self.log_with_history(self.logger.debug, str(d))

    def log_with_history(self, func, msg):
        self.history.append(msg)
        func(msg)


class RetriableError(Exception):
    pass


class LogInError(Exception):
    pass
