import os
import json
from collections import defaultdict


class Data:
    def __init__(self, storage_file='visits.json'):
        self.storage_file = storage_file
        self.data = self.load()

    def load(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                raw = json.load(f)

            raw['unique_total'] = set(raw.get('unique_total', []))

            for key in ['unique_daily', 'unique_monthly', 'unique_yearly']:
                raw[key] = defaultdict(set, {k: set(v) for k, v in raw.get(key, {}).items()})

            for key in ['daily', 'monthly', 'yearly']:
                raw[key] = defaultdict(int, raw.get(key, {}))

            raw['by_region'] = defaultdict(int, raw.get('by_region', {}))
            raw['unique_by_region'] = defaultdict(set, {
                k: set(v) for k, v in raw.get('unique_by_region', {}).items()
            })

            return raw

        return {
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

    def save(self):
        data_to_save = {
            'total': self.data['total'],
            'unique_total': list(self.data['unique_total']),
            'daily': dict(self.data['daily']),
            'monthly': dict(self.data['monthly']),
            'yearly': dict(self.data['yearly']),
            'unique_daily': {k: list(v) for k, v in self.data['unique_daily'].items()},
            'unique_monthly': {k: list(v) for k, v in self.data['unique_monthly'].items()},
            'unique_yearly': {k: list(v) for k, v in self.data['unique_yearly'].items()},
            'by_region': dict(self.data['by_region']),
            'unique_by_region': {k: list(v) for k, v in self.data['unique_by_region'].items()}
        }

        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
