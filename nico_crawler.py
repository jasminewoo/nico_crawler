import os
import logging

from MyList import MyList
from Video import Video

log = logging.getLogger(__name__)

if __name__ == '__main__':
    url = 'http://www.nicovideo.jp/mylist/48382005'

    if not os.path.exists('config.json'):
        raise FileNotFoundError(
            'config not found. Create a json file with the following details: download_location, email, password')

    videos = []
    if 'mylist' in url:
        ml = MyList(url)
        videos = ml.videos
    else:
        videos = [Video(url)]

    for video in videos:
        log.info('Start {}'.format(video))
        video.download()
        log.info('Done  {}'.format(video))