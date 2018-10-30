import base64
import logging
import os
import unicodedata
from urllib.error import URLError

from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError, DownloadError

from core import config
from core.utils import string_utils

logging.getLogger('niconico').setLevel('CRITICAL')
logging.getLogger('youtube_dl').setLevel('CRITICAL')

k_DOWNLOADS_FOLDER_PATH = 'downloads'


class CustomYoutubeDL(YoutubeDL):
    def __init__(self, video, logger=None):
        params = get_ydl_options(video=video, logger=logger)
        logger.debug("outtmpl='{}'".format(params['outtmpl']))
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
            if not ydl.path:
                logger.debug('Download completed but the file is not there; cannot upload to cloud')
                raise RetriableError
            logger.debug('Now uploading the file to cloud...')
            filename = sanitize_title(ydl.filename)
            storage.upload_file(filename, ydl.path)
            logger.debug('Upload done')
    except (URLError, ExtractorError, DownloadError, MemoryError) as e:
        if 'Niconico videos now require logging in' in str(e):
            raise LogInError
        else:
            logger.debug(e)
            raise RetriableError
    finally:
        if storage and ydl.path:
            ydl.remove_local_file()


def sanitize_title(title):
    title = unicodedata.normalize('NFKC', title)
    for key, value in config.global_instance['title_sanitization'].items():
        if key in title:
            title = title.replace(key, value)
    while '  ' in title:
        title = title.replace('  ', ' ')
    return title


def encode_title(video_title):
    return base64.urlsafe_b64encode(str.encode(video_title)).decode()


def decode_title(b64str):
    return base64.urlsafe_b64decode(b64str.encode()).decode()


def get_ydl_options(video, logger=None):
    title = string_utils.multi_replace(video.title, {'/': '-', '%': '％'}) if video.title else '%(title)s'
    options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '{}/%(upload_date)s-{}-%(id)s.%(ext)s'.format(k_DOWNLOADS_FOLDER_PATH, title),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': config.global_instance['convert_to'] if 'convert_to' in config.global_instance else 'm4a',
            'preferredquality': '320',
        }]
    }

    if logger:
        cl = logger if type(logger) is CustomLogger else CustomLogger(logger=logger)
        options['logger'] = cl
        options['progress_hooks']: [cl.hook]

    if video.login_failed:
        if config.global_instance.has_nico_creds():
            nc = config.global_instance.get_random_nico_creds()
            options['username'] = nc.username
            options['password'] = nc.password
            logger.debug(video.video_id + ' login failed previously; logging in this time with ' + nc.username)
        else:
            raise LogInError(video.video_id + ' login failed previously, but nicovideo credentials not provided')

    return options


class CustomLogger:
    def __init__(self, logger):
        self.logger = logger
        self.history = []

    def debug(self, msg):
        self.log(self.logger.debug, msg)

    def warning(self, msg):
        self.log(self.logger.debug, msg)

    def error(self, msg):
        self.log(self.logger.debug, msg)

    def hook(self, d):
        pass

    def log(self, func, msg, append_to_history=False):
        if append_to_history:
            self.history.append(msg)
        func(msg)


class RetriableError(Exception):
    pass


class LogInError(RetriableError):
    pass
