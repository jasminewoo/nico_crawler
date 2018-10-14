import html as html_lib
import json
import logging
import re

import requests

logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('youtube-dl').setLevel('CRITICAL')
log = logging.getLogger(__name__)
url_regex_str = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


class Video:
    k_VIDEO_TYPE_UTATTEMITA = 'utattemita'
    k_VIDEO_TYPE_VOCALOID_ORG = 'org'
    k_VIDEO_TYPE_UNKNOWN = 'unknown'

    def __init__(self, video_id=None, url=None, mylist_count=None):
        if (1 if video_id else 0) + (1 if url else 0) != 1:
            raise AssertionError('Need one of video_id and url')
        if url:
            self.video_id = url.split('/')[-1].split('?')[0]
        if video_id:
            self.video_id = video_id
        self._http_response = None
        self._video_json = None
        self.requires_creds = False
        self._mylist_count = mylist_count

    def get_related_urls(self):
        urls = []
        vt = self.video_type
        if vt == self.k_VIDEO_TYPE_UTATTEMITA:
            matches = re.findall(url_regex_str, self.description)
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
    def requires_login(self):
        return self.requires_creds or \
               'メールアドレスまたは電話番号' in self.html

    @property
    def url(self):
        return 'http://www.nicovideo.jp/watch/' + self.video_id

    @property
    def video_type(self):
        tags = self.tags
        if '歌ってみた' in tags:
            return self.k_VIDEO_TYPE_UTATTEMITA
        elif 'VOCALIOD' in tags:
            return self.k_VIDEO_TYPE_VOCALOID_ORG
        else:
            return self.k_VIDEO_TYPE_UNKNOWN

    @property
    def description(self):
        if self.video_json:
            return self.video_json['video']['description']

        # tag1 = '<meta itemprop="description" content="'
        tag2 = '<p class="VideoDescription-text" itemprop="description">'
        if tag2 in self.html:
            idx_start = self.html.index(tag2) + len(tag2)
            idx_end = self.html.index('\n', idx_start) - len('</p>')
            return self.html[idx_start:idx_end]
        else:
            log.debug('{} has no description'.format(self.video_id))

    @property
    def is_deleted_or_private(self):
        return self.http_status_code == 403 or \
               self.http_status_code == 404 or \
               'ページが見つかりませんでした' in self.html or \
               'お探しの動画は再生できません' in self.html or \
               'Unable to play video' in self.html or \
               '動画が投稿されている公開コミュニティ一覧' in self.html or \
               'チャンネル会員専用動画' in self.html

    @property
    def mylist_count(self):
        if self.is_deleted_or_private:
            return 0

        if not self._mylist_count:
            if self.video_json.requires_creds:
                self._mylist_count = int(self.video_json['video']['mylistCount'])
            else:
                if 'mylistCount' in self.html:
                    idx_start = self.html.index('mylistCount')
                    idx_start = self.html.index(':', idx_start)
                    idx_end = self.html.index(',', idx_start)
                    self._mylist_count = int(self.html[idx_start + 1:idx_end])
                elif 'MylistCountMeta-counter' in self.html:
                    start_str = 'MylistCountMeta-counter"><span class="FormattedNumber">'
                    idx_start = self.html.index(start_str) + len(start_str)
                    idx_end = self.html.index('</span>', idx_start)
                    self._mylist_count = int(self.html[idx_start:idx_end].replace(',', ''))
                else:
                    raise ValueError('{} has no mylist count'.format(self.video_id))
        return self._mylist_count

    @property
    def http_status_code(self):
        if not self._http_response:
            self._http_response = requests.get(self.url)
        return self._http_response.status_code

    @property
    def html(self):
        if not self._http_response:
            self._http_response = requests.get(self.url)
        return html_lib.unescape(str(self._http_response.text)) + str(self._http_response)

    @property
    def video_json(self):
        if not self._video_json:
            if self.html:
                for line in self.html.split('\n'):
                    json_tag = '<div id="js-initial-watch-data"'
                    if json_tag in line:
                        idx_start = line.index('data-api-data="') + len('data-api-data="')
                        idx_end = line.index('" data-environment', idx_start)
                        self._video_json = json.loads(line[idx_start:idx_end])
        return self._video_json

    @property
    def tags(self):
        if self.video_json:
            return list(map(lambda x: x['name'], self.video_json['tags']))

        lines = self.html.split('\n')
        for line in lines:
            line = line.strip().strip('\t').strip()
            if line.startswith('<meta name="keywords"'):
                idx_start = len('<meta name="keywords" content="')
                return line[idx_start:-2].split(',')
        return []

    def __str__(self):
        return self.video_id
