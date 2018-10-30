from core import download_thread
from core.html_handler.video_html_parser import VideoHTMLParser
from core.model.video import Video
from tests.custom_test_case import CustomTestCase

k_VIDEO_HTML = 'video2.html'


class DownloadThreadTest(CustomTestCase):
    def test_contains_banned_keywords_positive(self):
        html_string = self.get_resource_contents(k_VIDEO_HTML)
        v = Video(video_id='fake_id_123')
        v._html = VideoHTMLParser(html_string=html_string)
        contains = download_thread._title_contains_keywords(video=v, keywords=['そう'])
        self.assertTrue(contains, 'The title contains the banned keyword')

    def test_contains_banned_keywords_negative(self):
        html_string = self.get_resource_contents(k_VIDEO_HTML)
        v = Video(video_id='fake_id_123')
        v._html = VideoHTMLParser(html_string=html_string)
        contains = download_thread._title_contains_keywords(video=v, keywords=['keyword1', 'keyword2'])
        self.assertFalse(contains, 'The title does not contain the banned keyword')
