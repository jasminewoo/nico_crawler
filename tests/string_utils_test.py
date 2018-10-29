import unittest

from core.utils import string_utils


class StringUtilsTest(unittest.TestCase):
    def test_multi_replace(self):
        org_str = 'replace me'
        replace_definition = {'replace': 'result', 'me': 'success'}
        new_str = string_utils.multi_replace(org_str, replace_definition)
        self.assertEqual('result success', new_str)

    def test_contains_substrings_null_substrings(self):
        args = [
            {},
            None
        ]
        for arg in args:
            with self.subTest(str(arg)):
                try:
                    string_utils.contains_any_of_substrings('mystring', arg)
                except AssertionError as e:
                    self.assertEqual("'substrings' must be a list", str(e))
