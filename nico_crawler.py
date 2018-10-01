import json
import requests

from MyList import MyList
from Video import Video

if __name__ == '__main__':
    url = 'http://www.nicovideo.jp/mylist/48382005'

    videos = []
    if 'mylist' in url:
        ml = MyList(url)
        videos = ml.videos
    else:
        videos = [Video(url)]
