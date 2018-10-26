import unittest

from core import custom_youtube_dl


class CustomYoutubeDLTest(unittest.TestCase):

    def test_filename_sanitize(self):
        kvps = {
            'メトロノーム 歌ってみた / pazi': 'メトロノーム 歌ってみた pazi',
        }
        for org_title, expected in kvps.items():
            actual = custom_youtube_dl.sanitize_title(org_title)
            self.assertEqual(expected, actual)
