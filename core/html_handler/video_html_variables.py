from html import unescape

from core.html_handler.html_variable import HTMLVariable, HTMLVariableCollection
from core.html_handler.nico_html_parser import ServiceUnderMaintenanceError


class Tags(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[{'meta.name': 'keywords'}], data_key='content')

    def postprocess(self):
        if self.data != '':
            self.data = self.data.split(',')
        else:
            self.data = []


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


class VideoJson(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[{'div.id': 'js-initial-watch-data'}], data_key='data-api-data')

    def postprocess(self):
        import json
        self.data = json.loads(self.data)


class LoginForm(HTMLVariable):
    def __init__(self):
        HTMLVariable.__init__(self, tag_conditions=[{'form.method': 'POST', 'form.id': 'login_form'}])

    @property
    def is_present(self):
        return self.data is not None


class Message(HTMLVariableCollection):
    def __init__(self):
        HTMLVariableCollection.__init__(self, [
            HTMLVariable(tag_conditions=[{'div.id': 'PAGEBODY'}]),
            HTMLVariable(tag_conditions=[{'p.class': 'messageTitle'}])
        ])

    def postprocess(self):
        unescaped = unescape(self.data)
        if 'Currently under maintenance' in unescaped or 'ただいまメンテナンス中です' in unescaped:
            raise ServiceUnderMaintenanceError

    @property
    def is_private_or_deleted(self):
        if self.data:
            unescaped = unescape(self.data)
            return 'Unable to play video' in unescaped or \
                   'This video does not exist, or has been deleted' in unescaped or \
                   'ページが見つかりませんでした' in unescaped or \
                   'お探しの動画は再生できません' in unescaped
        return False


class Description(HTMLVariableCollection):
    def __init__(self):
        HTMLVariableCollection.__init__(self, [
            HTMLVariable(tag_conditions=[{'p.class': 'VideoDescription-text', 'p.itemprop': 'description'}]),
            HTMLVariable(tag_conditions=[{'meta.itemprop': 'description'}], data_key='content'),
            HTMLVariable(tag_conditions=[{'meta.name': 'description'}], data_key='content')
        ])
