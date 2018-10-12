import re
import requests

from core import global_config
from core.video import Video

k_MYLIST_PATTERN = re.compile('(?<=<a href="/mylistcomment/video/)(.*?)">(.*?)(?=</a>)')


class Ranking:
    def __init__(self, url):
        self.url = url

    @property
    def videos(self):
        vids = []
        r = requests.get(self.url)
        items = list(filter(lambda line: '<div class="itemData">' in line, str(r.text).split('\n')))
        for item in items:
            matches = k_MYLIST_PATTERN.search(item)
            video_id_pos = list(matches.regs[0])
            video_id_pos[1] = item.index('">', video_id_pos[0])
            video = Video(video_id=item[video_id_pos[0]:video_id_pos[1]])
            vids.append(video)
        return vids
