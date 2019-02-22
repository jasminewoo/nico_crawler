import re

import requests

from core import config
from core.model.video import Video

k_MYLIST_PATTERN = re.compile('(?<=<a href="/mylistcomment/)(.*?)">(.*?)(?=</a>)')


class Search:
    def __init__(self, url):
        self.url = url.split('?')[0]

    def __str__(self):
        return '/'.join(self.url.split('/')[-2:])

    @property
    def videos(self):
        break_now = False
        vids = []
        for page in range(1, 99):
            if break_now:
                break

            url = '{}?page={}&sort=m&order=d'.format(self.url, page)
            r = requests.get(url)
            links = str(r.text).split('<li class="item" data-video-item data-video-id="')
            if len(links) == 1:
                break

            for link in links:
                line_split = link.split('" data-nicoad-video')
                video_id = line_split[0]

                if len(video_id) > 20:
                    continue

                if len(line_split) > 1:
                    rest = line_split[1]
                    pos = k_MYLIST_PATTERN.search(rest).regs[-1]
                    mylist_count = int(rest[pos[0]:pos[1]].replace(',', ''))
                    if mylist_count >= config.global_instance['minimum_mylist']:
                        vid = Video(video_id=video_id, mylist_count=mylist_count)
                        vids.append(vid)
                    else:
                        break_now = True
                        break

        return vids
