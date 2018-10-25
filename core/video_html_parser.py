import json
import logging
from html.parser import HTMLParser
from html import unescape

import requests

logging.getLogger('urllib3').setLevel('CRITICAL')


class VideoHTMLParser(HTMLParser):
    def __init__(self, url=None, html_string=None):
        HTMLParser.__init__(self)
        self.video_json = None
        self.title_detected = False
        self.directed_to_login_page = False
        self.message_title_detected = False
        self._is_deleted_or_private = False
        self.mylist_count_detection_phase = 0
        self._mylist_count_backup = None
        self._tags_backup = None
        self._description_backup = None

        if url:
            r = requests.get(url)
            self.status_code = r.status_code
            self.html_string = unescape(str(r.text))
        elif html_string:
            self.status_code = 0
            self.html_string = unescape(html_string)
        else:
            raise AssertionError('No info provided')

        self.feed(self.html_string)

    @property
    def description(self):
        if not self.is_available:
            return ''
        return self.video_json['video']['description'] if self.video_json else self._description_backup

    @property
    def tags(self):
        if not self.is_available:
            return []
        return list(map(lambda x: x['name'], self.video_json['tags'])) if self.video_json else self._tags_backup

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.title_detected = True
        elif tag == 'div':
            attrs = dict(attrs)
            if 'id' in attrs and 'data-api-data' in attrs:
                if attrs['id'] == 'js-initial-watch-data':
                    json_string = unescape(attrs['data-api-data'])
                    self.video_json = json.loads(json_string)
        elif tag == 'span':
            attrs = dict(attrs)
            if 'class' in attrs:
                if self.mylist_count_detection_phase == 1 and attrs['class'] == 'FormattedNumber':
                    self.mylist_count_detection_phase = 2
                if attrs['class'] == 'MylistCountMeta-counter':
                    self.mylist_count_detection_phase = 1
        elif tag == 'meta':
            attrs = dict(attrs)
            if 'name' in attrs and 'content' in attrs:
                if attrs['name'] == 'keywords':
                    self._tags_backup = attrs['content'].split(',')
                elif attrs['name'] == 'description':
                    self._description_backup = attrs['content']
            if 'itemprop' in attrs and 'content' in attrs:
                if attrs['itemprop'] == 'description':
                    self._description_backup = unescape(attrs['content'])
        elif tag == 'p':
            attrs = dict(attrs)
            if 'class' in attrs:
                if attrs['class'] == 'messageTitle':
                    self.message_title_detected = True

    def handle_data(self, data):
        if self.title_detected:
            self.directed_to_login_page = 'ログイン' in data
            self.title_detected = False
        elif self.mylist_count_detection_phase == 2:
            self._mylist_count_backup = int(data.replace(',', ''))
            self.mylist_count_detection_phase = 0
        elif self.message_title_detected:
            if data == 'お探しの動画は再生できません':
                self._is_deleted_or_private = True
            self.message_title_detected = False

    def error(self, message):
        raise RuntimeError(message)

    @property
    def is_available(self):
        unavailable = self._is_deleted_or_private or \
                      self.status_code == 403 or \
                      self.status_code == 404 or \
                      self.directed_to_login_page or \
                      'ページが見つかりませんでした' in self.html_string or \
                      'お探しの動画は再生できません' in self.html_string or \
                      'Unable to play video' in self.html_string or \
                      'This video does not exist, or has been deleted' in self.html_string or \
                      '動画が投稿されている公開コミュニティ一覧' in self.html_string or \
                      'チャンネル会員専用動画' in self.html_string or \
                      'メールアドレスまたは電話番号' in self.html_string
        return not unavailable

    @property
    def mylist_count(self):
        if not self.is_available:
            return 0
        return int(self.video_json['video']['mylistCount']) if self.video_json else self._mylist_count_backup
