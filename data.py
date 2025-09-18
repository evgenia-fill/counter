import os
import json
from collections import defaultdict

class Data:
    def __init__(self, storage_file='visits.json'):
        self.storage_file = storage_file
        self.data = self.load()

    @staticmethod
    def load(storage_file='visits.json'):
        if os.path.exists(storage_file):
            with open(storage_file, 'r') as f:
                data = json.load(f)

                data['unique_total'] = set(data['unique_total'])
                for key in ['unique_daily', 'unique_monthly', 'unique_yearly']:
                    data[key] = defaultdict(set, {
                        k: set(v) for k, v in data[key].items()
                    })

                return data

        return {
            'total': 0,
            'unique_total': set(),
            'daily': defaultdict(int),
            'monthly': defaultdict(int),
            'yearly': defaultdict(int),
            'unique_daily': defaultdict(set),
            'unique_monthly': defaultdict(set),
            'unique_yearly': defaultdict(set)
        }

    def save(self):
        data_to_save = self.data.copy()
        data_to_save['unique_total'] = list(self.data['unique_total'])

        for key in ['unique_daily', 'unique_monthly', 'unique_yearly']:
            data_to_save[key] = {k: list(v) for k, v in self.data[key].items()}

        with open(self.storage_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)