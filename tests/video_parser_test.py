import unittest

from core.html_handler.nico_html_parser import ServiceUnderMaintenanceError
from core.html_handler.video_html_parser import VideoHTMLParser
from tests.custom_test_case import CustomTestCase

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
k_ENG = 'video_with_json_eng.html'


class VideoParserTest(CustomTestCase):
    def test_json_detection(self):
        p = self.get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertIsNotNone(p.video_json)

    def test_normal_title(self):
        p = self.get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertEqual('え？あぁ、そう。　歌ってみた－遊 - ニコニコ動画', p.html_vars['title'].data)

    def test_login_redirect_title(self):
        p = self.get_parser(k_LOGIN_PAGE)
        self.assertTrue(p.html_vars['title'].is_login_page, 'This is a login page')

    def test_login_redirect_is_available(self):
        p = self.get_parser(k_LOGIN_PAGE)
        self.assertFalse(p.is_available, 'The video should not be identified as available')
        self.assertEqual([], p.tags)
        self.assertEqual('', p.description)

    def test_mylist_with_json(self):
        p = self.get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertEqual(5850, p.mylist_count)

    def test_mylist_without_json(self):
        p = self.get_parser(k_UTATTEMITA_WITHOUT_JSON)
        self.assertEqual(2954, p.mylist_count)

    def test_tags_without_json(self):
        p = self.get_parser(k_UTATTEMITA_WITHOUT_JSON)
        self.assertIsNotNone(p.tags)
        self.assertEqual('歌ってみた', p.tags[0])

    def test_tags_with_json(self):
        p = self.get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertIsNotNone(p.tags)
        self.assertEqual('歌ってみた', p.tags[0])

    def test_desc_with_json(self):
        p = self.get_parser(k_UTATTEMITA_WITH_JSON)
        self.assertIsNotNone(p.description)
        contains = '歌わせて頂きました' in p.description
        self.assertTrue(contains, "'歌わせて頂きました' should be in the description")
        contains = 'https://www.nicovideo.jp/watch/sm10122021' in p.description
        self.assertTrue(contains, "'https://www.nicovideo.jp/watch/sm10122021' should be in the description")

    def test_desc_without_json(self):
        p = self.get_parser(k_UTATTEMITA_WITHOUT_JSON)
        self.assertIsNotNone(p.description)
        contains = 'どうぞよろしくお願い致します' in p.description
        self.assertTrue(contains, "'どうぞよろしくお願い致します' should be in the description")
        contains = 'https://www.nicovideo.jp/mylist/30043188' in p.description
        self.assertTrue(contains, "'https://www.nicovideo.jp/mylist/30043188' should be in the description")

    def test_maint_exception(self):
        for filename in [k_MAINT_JA, k_MAINT_EN]:
            with self.subTest(filename):
                self.assertRaises(ServiceUnderMaintenanceError, self.get_parser, filename)

    def test_maint_exception_by_status_code(self):
        # Regular page but with http code 503
        self.assertRaises(ServiceUnderMaintenanceError, self.get_parser, k_UTATTEMITA_WITH_JSON, 503)

    def test_deleted_video_identified_as_unavailable(self):
        p = self.get_parser(k_DELETED)
        self.assertFalse(p.is_available, 'The video should not be marked as available')
        self.assertEqual([], p.tags, 'The video should return empty list for tags')
        self.assertEqual('', p.description, 'The video should return an empty description')
        self.assertEqual(0, p.mylist_count, 'The video should return 0 mylist count')

    def test_videos_with_zero_tags(self):
        for filename in [k_ZERO_TAGS_WITH_JSON, k_ZERO_TAGS_WITHOUT_JSON]:
            with self.subTest(filename):
                p = self.get_parser(filename)
                self.assertEqual([], p.tags, 'tags should be an empty list')

    def test_private_identified_as_unavailable(self):
        for filename in [k_PRIVATE_EN, k_PRIVATE_JA]:
            with self.subTest(filename):
                p = self.get_parser(filename)
                self.assertFalse(p.is_available, 'Video should not be identified as available')

    def test_blank_video(self):
        self.get_parser(k_BLANK)
        # If the parser initializes without any error, then good.

    def test_channel_members_only_identified_as_unavailable(self):
        p = self.get_parser(k_CHANNEL_ONLY)
        self.assertFalse(p.is_available, 'Video should not be identified as available')

    def test_not_authorized_by_message(self):
        p = self.get_parser(k_NOT_AUTHORIZED)
        self.assertFalse(p.is_available, 'Video should not be identified as available')

    def test_not_authorized_by_status_code(self):
        for code in [403, 404]:
            with self.subTest(code):
                p = self.get_parser(k_UTATTEMITA_WITH_JSON, status_code=code)
                self.assertFalse(p.is_available, 'Video should not be identified as available')

    def test_original_title_with_eng_translation(self):
        p = self.get_parser(k_ENG)
        self.assertEqual('夜もすがら君想ふ　歌ってみた　【夏代孝明とnqrse】', p.video_title)

    def get_parser(self, filename, status_code=0):
        html_string = self.get_resource_contents(path=filename)
        return VideoHTMLParser(html_string=html_string, status_code=status_code)


if __name__ == '__main__':
    unittest.main()
