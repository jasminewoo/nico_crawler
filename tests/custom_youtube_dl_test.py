from core import custom_youtube_dl
from core.html_handler.video_html_parser import VideoHTMLParser
from core.model.video import Video
from tests.custom_test_case import CustomTestCase

k_VIDEO_WITH_ILLEGAL_TITLE = 'video2_with_illegal_characters_in_title.html'


class CustomYoutubeDLTest(CustomTestCase):

    def test_filename_sanitize(self):
        kvps = {
            'メトロノーム 歌ってみた / pazi': 'メトロノーム 歌ってみた pazi',
            '【覚えて歌お！】カラオケで歌えるボーカロイド曲集09_4月号B': '[覚えて歌お!]カラオケで歌えるボーカロイド曲集09_4月号B',
            '【2人で】ン（Ver）【初心者Fとmorlbon】': '[2人で]ン(Ver)[初心者Fとmorlbon]',
            '２５２５': '2525',
            'ニコニコ動画流星群　ﾏｯﾀﾘ歌ってみた　旦_(-ω- ,,)　　【 リツカ 】': 'ニコニコ動画流星群 マッタリ歌ってみた 旦_(-ω- ,,) [ リツカ ]',
            '〜': '~',
            'ｂｙ': 'by',
            '＿': '_'
        }
        for org_title, expected in kvps.items():
            with self.subTest(org_title):
                actual = custom_youtube_dl.sanitize_title(org_title)
                self.assertEqual(expected, actual)

    def test_title_transformation_null_title(self):
        v = Video(video_id='sm')
        params = custom_youtube_dl.get_ydl_options(video=v)
        self.assertTrue('%(title)s' in params['outtmpl'], "'%(title)s' should be in 'outtmpl'")

    def test_title_transformation_real_title(self):
        p = VideoHTMLParser(html_string=self.get_resource_contents(k_VIDEO_WITH_ILLEGAL_TITLE))
        v = Video(video_id='sm')
        v._html = p
        params = custom_youtube_dl.get_ydl_options(video=v)
        self.assertTrue('-％' in params['outtmpl'], "'-％' should be in 'outtmpl'")
        self.assertFalse('%(title)s' in params['outtmpl'], "'%(title)s' should not be in 'outtmpl'")
