class Statistics:
    def __init__(self, data_store):
        self.data = data_store.data

    def get_stats(self, period='total'):
        if period == 'total':
            return {
                'total': self.data['total'],
                'unique': len(self.data['unique_total'])
            }

        elif period == 'yearly':
            return {
                year: {
                    'total': self.data['yearly'][year],
                    'unique': len(self.data['unique_yearly'].get(year, set()))
                } for year in self.data['yearly']
            }

        elif period == 'monthly':
            return {
                month: {
                    'total': self.data['monthly'][month],
                    'unique': len(self.data['unique_monthly'].get(month, set()))
                } for month in self.data['monthly']
            }

        elif period == 'daily':
            return {
                day: {
                    'total': self.data['daily'][day],
                    'unique': len(self.data['unique_daily'].get(day, set()))
                } for day in self.data['daily']
            }

        else:
            return {'error': 'Invalid period'}
