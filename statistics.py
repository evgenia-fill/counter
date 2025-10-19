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

        elif period == 'regionally':
            return {
                region: {
                    'total': self.data['by_region'][region],
                    'unique': len(self.data['unique_by_region'].get(region, set()))
                } for region in self.data['by_region']
            }

        elif period == 'by_browser':
            return {
                browser: {
                    'total': self.data['by_browser'][browser],
                    'unique': len(self.data['unique_by_browser'].get(browser, set()))
                } for browser in self.data['by_browser']
            }

        else:
            return {'error': 'Invalid period'}
