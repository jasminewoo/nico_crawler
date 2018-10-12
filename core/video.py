import logging
import re

import requests

logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('youtube-dl').setLevel('CRITICAL')
log = logging.getLogger(__name__)


class Video:
    k_VIDEO_TYPE_UTATTEMITA = 'utattemita'
    k_VIDEO_TYPE_VOCALOID_ORG = 'org'
    k_VIDEO_TYPE_UNKNOWN = 'unknown'

    def __init__(self, video_id=None, url=None):
        if (1 if video_id else 0) + (1 if url else 0) != 1:
            raise AssertionError('Need one of video_id and url')
        if url:
            self.video_id = url.split('/')[-1].split('?')[0]
        if video_id:
            self.video_id = video_id
        self._html = None
        self.requires_creds = False

    def get_related_urls(self):
        urls = []
        vt = self.video_type
        if vt == self.k_VIDEO_TYPE_UTATTEMITA:
            desc = self.description
            matches = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', desc)
            for url in matches:
                if 'nicovideo' not in url:
                    continue
                if '/watch/' in url or '/mylist/' in url:
                    urls.append(url)
        else:
            search_template = 'https://www.nicovideo.jp/search/{}%20%E6%AD%8C%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%9F'
            urls.append(search_template.format(self.video_id))

        return urls

    @property
    def url(self):
        return 'http://www.nicovideo.jp/watch/' + self.video_id

    @property
    def video_type(self):
        tags = self.get_tags()
        if '歌ってみた' in tags:
            return self.k_VIDEO_TYPE_UTATTEMITA
        elif 'VOCALIOD' in tags:
            return self.k_VIDEO_TYPE_VOCALOID_ORG
        else:
            return self.k_VIDEO_TYPE_UNKNOWN

    @property
    def description(self):
        tag1 = '<meta itemprop="description" content="'
        tag2 = '<p class="VideoDescription-text" itemprop="description">'

        if tag2 in self.html:
            idx_start = self.html.index(tag1) + len(tag1)
            idx_end = self.html.index('\n', idx_start) - len('</p>')
            return self.html[idx_start:idx_end]
        else:
            log.debug('{} has no description'.format(self.video_id))

    @property
    def mylist(self):
        if 'mylistCount' in self.html:
            idx_start = self.html.index('mylistCount')
            idx_start = self.html.index(':', idx_start)
            idx_end = self.html.index(',', idx_start)
            return int(self.html[idx_start + 1:idx_end])
        elif 'MylistCountMeta-counter' in self.html:
            start_str = 'MylistCountMeta-counter"><span class="FormattedNumber">'
            idx_start = self.html.index(start_str) + len(start_str)
            idx_end = self.html.index('</span>', idx_start)
            return int(self.html[idx_start:idx_end].replace(',', ''))
        else:
            log.debug('{} has no mylist count'.format(self.video_id))
            return 0

    @property
    def html(self):
        if not self._html:
            r = requests.get(self.url)
            self._html = str(r.text)
        return self._html

    def get_tags(self):
        lines = self.html.split('\n')
        for line in lines:
            line = line.strip().strip('\t').strip()
            if line.startswith('<meta name="keywords"'):
                idx_start = len('<meta name="keywords" content="')
                return line[idx_start:-2].split(',')
        return []

    def __str__(self):
        return self.video_id
