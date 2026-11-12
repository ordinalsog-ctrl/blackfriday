import collections
import csv
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_benchmark120', ROOT / 'tools/build_benchmark120.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestBenchmark120(unittest.TestCase):
    def test_fixed_reproducible_sample(self):
        source = ROOT / 'data/produktstamm_500_kandidaten.csv'
        sample = module.build(source)
        self.assertEqual(len(sample), 120)
        self.assertEqual(sample, module.build(source))
        self.assertEqual(len({r['product_id'] for r in sample}), 120)
        self.assertEqual(collections.Counter(r['category'] for r in sample), collections.Counter(module.QUOTAS))
        self.assertTrue(all(r['benchmark_eligibility']=='DISCOVERY_ONLY' for r in sample))
        self.assertTrue(all(r['provider_match_status']=='NOT_TESTED' for r in sample))

    def test_committed_csv_matches_generator(self):
        expected = module.build(ROOT / 'data/produktstamm_500_kandidaten.csv')
        with (ROOT / 'data/api_benchmark_120_candidates.csv').open(newline='', encoding='utf-8') as f:
            actual = list(csv.DictReader(f))
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
