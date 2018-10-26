import unittest

from core import custom_youtube_dl


class CustomYoutubeDLTest(unittest.TestCase):

    def test_filename_sanitize(self):
        kvps = {
            'メトロノーム 歌ってみた / pazi': 'メトロノーム 歌ってみた pazi',
            '【覚えて歌お！】カラオケで歌えるボーカロイド曲集09_4月号B': '[覚えて歌お!]カラオケで歌えるボーカロイド曲集09_4月号B',
            '【2人で】ン（Ver）【初心者Fとmorlbon】':'[2人で]ン(Ver)[初心者Fとmorlbon]'
        }
        for org_title, expected in kvps.items():
            with self.subTest(org_title):
                actual = custom_youtube_dl.sanitize_title(org_title)
                self.assertEqual(expected, actual)
