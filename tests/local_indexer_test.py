import os
import unittest

from core.indexer.local import LocalIndexer
from core.utils.path_utils import get_root_prefix

k_FILENAME = 'unittest_local_indexer'


class LocalIndexerTest(unittest.TestCase):
    def setUp(self):
        self.indexer = LocalIndexer({'filename': k_FILENAME})

    def test_insert(self):
        self.assertFalse(self.indexer.exists('vid1'), "The indexer should be empty")
        self.indexer.set_status('vid1', 'pending')
        self.assertTrue(self.indexer.exists('vid1'), "'vid1' must exist in the indexer")

    def test_insert_multiple(self):
        self.indexer.set_status('vid1', 'pending')
        self.indexer.set_status('vid2', 'pending')
        self.assertTrue(self.indexer.exists('vid2'), "'vid2' must exist in the indexer")
        self.assertEqual(2, self.indexer.count)

    def test_replace_status(self):
        self.indexer.set_status('vid1', 'pending')
        self.assertEqual('pending', self.indexer.get_status('vid1'))
        self.indexer.set_status('vid1', 'done')
        self.assertEqual('done', self.indexer.get_status('vid1'))
        self.assertEqual(1, self.indexer.count)

    def tearDown(self):
        path = get_root_prefix() + k_FILENAME
        if os.path.exists(path):
            os.remove(path)
