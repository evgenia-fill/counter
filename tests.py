import unittest
from collections import defaultdict

import counter
from statistics import Statistics
from data import Data
import tempfile
import os


class TestCounter(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        self.temp_file.write('{}')
        self.temp_file.close()

        self.data_store = Data(storage_file=self.temp_file.name)
        if not self.data_store.data:
            self.data_store.data = {
                'total': 0,
                'unique_total': set(),
                'daily': defaultdict(int),
                'monthly': defaultdict(int),
                'yearly': defaultdict(int),
                'unique_daily': defaultdict(set),
                'unique_monthly': defaultdict(set),
                'unique_yearly': defaultdict(set),
                'by_region': defaultdict(int),
                'unique_by_region': defaultdict(set)
            }

        self.counter = counter.VisitCounter(storage_file=self.temp_file.name)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_data_save_load(self):
        self.data_store['total'] = 5
        self.data_store['unique_total'].add('v1')
        self.data_store.save()

        loaded = Data(self.temp_file.name)
        self.assertEqual(loaded['total'], 5)
        self.assertIn('v1', loaded['unique_total'])

    def test_stats_total(self):
        self.data_store['total'] = 10
        self.data_store['unique_total'] = {'v1', 'v2'}
        stats = Statistics(self.data_store)
        result = stats.get_stats('total')
        self.assertEqual(result['total'], 10)
        self.assertEqual(result['unique'], 2)

    def test_add_visit(self):
        self.counter.add_visit('visitor1', region='Russia')
        self.counter.add_visit('visitor1', region='Russia')
        self.counter.add_visit('visitor2', region='Netherlands')

        stats_total = self.counter.get_stats('total')
        self.assertEqual(stats_total['total'], 3)
        self.assertEqual(stats_total['unique'], 2)

        stats_region = self.counter.get_stats('regionally')
        self.assertEqual(stats_region['Russia']['total'], 2)
        self.assertEqual(stats_region['Russia']['unique'], 1)
        self.assertEqual(stats_region['Netherlands']['total'], 1)
        self.assertEqual(stats_region['Netherlands']['unique'], 1)


if __name__ == "__main__":
    unittest.main()
