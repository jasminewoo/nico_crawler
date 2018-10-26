import unittest

from core.html_handler.nico_html_parser import ServiceUnderMaintenanceError
from core.html_handler.video_html_parser import VideoHTMLParser

k_UTATTEMITA_WITH_JSON = 'video2.html'
k_UTATTEMITA_WITHOUT_JSON = 'video3_without_json.html'
k_LOGIN_PAGE = 'video_requiring_login.html'
k_MAINT_JA = 'maint_japanese.html'
k_MAINT_EN = 'maint_english.html'
k_DELETED = 'video_deleted.html'
k_ZERO_TAGS_WITHOUT_JSON = 'video_no_tags_no_json.html'
k_ZERO_TAGS_WITH_JSON = 'video_no_tags.html'
k_PRIVATE_JA = 'video_private_ja.html'
k_PRIVATE_EN = 'video_private_en.html'
k_BLANK = 'video_blank.html'
k_CHANNEL_ONLY = 'video_channel_members_only.html'
k_NOT_AUTHORIZED = 'video_not_authorized.html'


class VideoParserTest(unittest.TestCase):
    def test_json_detection(self):
        p = get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertIsNotNone(p.video_json)

    def test_normal_title(self):
        p = get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertEqual('え？あぁ、そう。　歌ってみた－遊 - ニコニコ動画', p.html_vars['title'].data)

    def test_login_redirect_title(self):
        p = get_parser(k_LOGIN_PAGE)
        self.assertTrue(p.html_vars['title'].is_login_page, 'This is a login page')

    def test_login_redirect_is_available(self):
        p = get_parser(k_LOGIN_PAGE)
        self.assertFalse(p.is_available, 'The video should not be identified as available')
        self.assertEqual([], p.tags)
        self.assertEqual('', p.description)

    def test_mylist_with_json(self):
        p = get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertEqual(5850, p.mylist_count)

    def test_mylist_without_json(self):
        p = get_parser(k_UTATTEMITA_WITHOUT_JSON)
        self.assertEqual(2954, p.mylist_count)

    def test_tags_without_json(self):
        p = get_parser(k_UTATTEMITA_WITHOUT_JSON)
        self.assertIsNotNone(p.tags)
        self.assertEqual('歌ってみた', p.tags[0])

    def test_tags_with_json(self):
        p = get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertIsNotNone(p.tags)
        self.assertEqual('歌ってみた', p.tags[0])

    def test_desc_with_json(self):
        p = get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertIsNotNone(p.description)
        contains = '歌わせて頂きました' in p.description
        self.assertTrue(contains, "'歌わせて頂きました' should be in the description")
        contains = 'https://www.nicovideo.jp/watch/sm10122021' in p.description
        self.assertTrue(contains, "'https://www.nicovideo.jp/watch/sm10122021' should be in the description")

    def test_desc_without_json(self):
        p = get_parser(k_UTATTEMITA_WITHOUT_JSON)
        self.assertIsNotNone(p.description)
        contains = 'どうぞよろしくお願い致します' in p.description
        self.assertTrue(contains, "'どうぞよろしくお願い致します' should be in the description")
        contains = 'https://www.nicovideo.jp/mylist/30043188' in p.description
        self.assertTrue(contains, "'https://www.nicovideo.jp/mylist/30043188' should be in the description")

    def test_maint_exception(self):
        for filename in [k_MAINT_JA, k_MAINT_EN]:
            self.assertRaises(ServiceUnderMaintenanceError, get_parser, filename)

    def test_maint_exception_by_status_code(self):
        # Regular page but with http code 503
        self.assertRaises(ServiceUnderMaintenanceError, get_parser, k_UTATTEMITA_WITH_JSON, 503)

    def test_deleted_video_identified_as_unavailable(self):
        p = get_parser(k_DELETED)
        self.assertFalse(p.is_available, 'The video should not be marked as available')
        self.assertEqual([], p.tags, 'The video should return empty list for tags')
        self.assertEqual('', p.description, 'The video should return an empty description')
        self.assertEqual(0, p.mylist_count, 'The video should return 0 mylist count')

    def test_videos_with_zero_tags(self):
        for filename in [k_ZERO_TAGS_WITH_JSON, k_ZERO_TAGS_WITHOUT_JSON]:
            p = get_parser(filename)
            self.assertEqual([], p.tags, 'tags should be an empty list')

    def test_private_identified_as_unavailable(self):
        for filename in [k_PRIVATE_EN, k_PRIVATE_JA]:
            p = get_parser(filename)
            self.assertFalse(p.is_available, '{}: Video should not be identified as available'.format(filename))

    def test_blank_video(self):
        get_parser(k_BLANK)
        # If the parser initializes without any error, then good.

    def test_channel_members_only_identified_as_unavailable(self):
        p = get_parser(k_CHANNEL_ONLY)
        self.assertFalse(p.is_available, 'Video should not be identified as available')

    def test_not_authorized_by_message(self):
        p = get_parser(k_NOT_AUTHORIZED)
        self.assertFalse(p.is_available, 'Video should not be identified as available')

    def test_not_authorized_by_status_code(self):
        for code in [403, 404]:
            p = get_parser(k_UTATTEMITA_WITH_JSON, status_code=code)
            self.assertFalse(p.is_available, 'Video should not be identified as available')


def get_parser(filename, status_code=0):
    html_string = get_html_string(filename)
    return VideoHTMLParser(html_string=html_string, status_code=status_code)


def get_html_string(filename):
    # TODO: generalize this method so the resources can be accessed from anywhere
    with open('resources/' + filename, 'r') as fp:
        html_string = fp.read()
    return html_string


if __name__ == '__main__':
    unittest.main()
