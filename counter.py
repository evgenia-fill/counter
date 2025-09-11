from aiohttp import web
import os
import json
from datetime import datetime
from collections import defaultdict


class VisitCounter:
    def __init__(self, storage_file='visits.json'):
        self.storage_file = storage_file
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
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


    def save_data(self):
        data_to_save = self.data.copy()
        data_to_save['unique_total'] = list(self.data['unique_total'])

        for key in ['unique_daily', 'unique_monthly', 'unique_yearly']:
            data_to_save[key] = {k: list(v) for k, v in self.data[key].items()}

        with open(self.storage_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)

    def add_visit(self, visitor_id):
        try:
            now = datetime.now()
            day_key = now.strftime('%Y-%m-%d')
            month_key = now.strftime('%Y-%m')
            year_key = now.strftime('%Y')

            self.data['total'] += 1
            self.data['daily'][day_key] += 1
            self.data['monthly'][month_key] += 1
            self.data['yearly'][year_key] += 1

            if visitor_id not in self.data['unique_total']:
                self.data['unique_total'].add(visitor_id)

            self.data['unique_daily'][day_key].add(visitor_id)
            self.data['unique_monthly'][month_key].add(visitor_id)
            self.data['unique_yearly'][year_key].add(visitor_id)

            self.save_data()
        except Exception as e:
            print(f"Error adding visit: {e}")

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

async def visit_handler(request):
    visitor_ip = request.remote
    request.app['counter'].add_visit(visitor_ip)
    return web.Response(
        text=f"Новое посещение! IP: {visitor_ip}\nОбщее количество посещений: {request.app['counter'].data['total']}")


async def stats_handler(request):
    try:
        period = request.query.get('period', 'total')
        if period not in ['total', 'yearly', 'monthly', 'daily']:
            return web.json_response({'error': 'Invalid period. Use: total, yearly, monthly, daily'}, status=400)

        stats = request.app['counter'].get_stats(period)
        return web.json_response(stats)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def favicon_handler(request):
    return web.Response(status=404)


async def not_found_handler(request):
    return web.Response(text="Страница не найдена", status=404)


async def init_app():
    app = web.Application()
    app['counter'] = VisitCounter()

    app.router.add_get('/', visit_handler)
    app.router.add_get('/visit', visit_handler)
    app.router.add_get('/stats', stats_handler)
    app.router.add_get('/favicon.ico', favicon_handler)

    return app

if __name__ == '__main__':
    print("   http://localhost:8080/ - Главная страница")
    print("   http://localhost:8080/visit - Добавить посещение")
    print("   http://localhost:8080/stats - Статистика (JSON)")
    print("   http://localhost:8080/stats?period=daily - Статистика по дням")
    web.run_app(init_app(), host='localhost', port=8080)