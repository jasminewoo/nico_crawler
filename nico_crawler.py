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

    if 'mylist' in url:
        videos = MyList(url).videos
    elif 'search' in url:
        pass
    else:
        videos = [Video(url=url)]

    # TODO thread pool ( 4 concurrent threads )

    for video in videos:
        log.info('Start {}'.format(video))
        try:
            video.download()
            log.info('Done  {}'.format(video))
        except Exception as e:
            log.info('Fail  {}'.format(video))
            log.exception(e)
