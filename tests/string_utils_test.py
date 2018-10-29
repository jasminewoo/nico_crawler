import unittest

from core.utils import string_utils


class StringUtilsTest(unittest.TestCase):
    def test_multi_replace(self):
        org_str = 'replace me'
        replace_definition = {'replace': 'result', 'me': 'success'}
        new_str = string_utils.multi_replace(org_str, replace_definition)
        self.assertEqual('result success', new_str)
