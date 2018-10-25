from core.html_handler.html_variable import HTMLVariable, HTMLVariableCollection
from core.html_handler.nico_html_parser import NicoHTMLParser
from html import unescape


class VideoHTMLParser(NicoHTMLParser):
    def create_html_vars(self):
        return {
            'title': Title(),
            'tags': Tags(),
            'mylist': MylistCount(),
            'msg': Message(),
            'json': VideoJson(),
            'desc': Description()
        }

    @property
    def is_available(self):
        unescaped = unescape(self.html_string)
        unavailable = self.status_code == 403 or \
                      self.status_code == 404 or \
                      self.html_vars['title'].is_login_page or \
                      self.html_vars['msg'].is_private_or_deleted or \
                      '動画が投稿されている公開コミュニティ一覧' in unescaped or \
                      'チャンネル会員専用動画' in unescaped or \
                      'メールアドレスまたは電話番号' in unescaped
        return not unavailable

    @property
    def video_json(self):
        return self.html_vars['json'].data

    @property
    def description(self):
        if not self.is_available:
            return ''
        return self.video_json['video']['description'] if self.video_json else self.html_vars['desc'].data

    @property
    def tags(self):
        if not self.is_available:
            return []
        if self.video_json:
            return list(map(lambda x: x['name'], self.video_json['tags']))
        else:
            return self.html_vars['tags'].data

    @property
    def mylist_count(self):
        if not self.is_available:
            return 0
        if self.video_json:
            return int(self.video_json['video']['mylistCount'])
        else:
            return self.html_vars['mylist'].data


class Tags(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[{'meta.name': 'keywords'}], data_key='content')

    def postprocess(self):
        self.data = self.data.split(',')


class MylistCount(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[
            {'span.class': 'MylistCountMeta-counter'},
            {'span.class': 'FormattedNumber'}
        ])

    def postprocess(self):
        self.data = int(self.data.replace(',', ''))


class Title(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[{'title': None}])

    def postprocess(self):
        self.data = self.data.replace('\n', ' ')
        while '  ' in self.data:
            self.data = self.data.replace('  ', ' ')
        self.data = self.data.strip()

    @property
    def is_login_page(self):
        if self.data:
            return 'ログイン' in self.data
        return False


class Message(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[{'p.class': 'messageTitle'}])

    def postprocess(self):
        self.data = unescape(self.data)

    @property
    def is_private_or_deleted(self):
        if self.data:
            return 'Unable to play video' in self.data or \
                   'This video does not exist, or has been deleted' in self.data or \
                   'ページが見つかりませんでした' in self.data or \
                   'お探しの動画は再生できません' in self.data
        return False


class VideoJson(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[{'div.id': 'js-initial-watch-data'}], data_key='data-api-data')

    def postprocess(self):
        import json
        self.data = json.loads(self.data)


class Description(HTMLVariableCollection):
    def __init__(self):
        HTMLVariableCollection.__init__(self, [
            HTMLVariable(tag_conditions=[{'p.class': 'VideoDescription-text', 'p.itemprop': 'description'}]),
            HTMLVariable(tag_conditions=[{'meta.itemprop': 'description'}], data_key='content'),
            HTMLVariable(tag_conditions=[{'meta.name': 'description'}], data_key='content')
        ])
