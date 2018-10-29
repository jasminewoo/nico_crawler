import unittest

from core.utils.path_utils import get_root_prefix


class CustomTestCase(unittest.TestCase):
    def get_resource_contents(self, path, open_mode='r'):
        prefix = get_root_prefix()
        with open(prefix + 'tests/resources/' + path.strip('/'), open_mode) as fp:
            return fp.read()
