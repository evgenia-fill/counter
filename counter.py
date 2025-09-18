from aiohttp import web
from datetime import datetime
from data import Data
from statistics import Statistics


class VisitCounter:
    def __init__(self, storage_file='visits.json'):
        self.storage_file = storage_file
        self.data = Data()
        self.stat = Statistics(self.data)

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

            self.data.save()
        except Exception as e:
            print(f"Error adding visit: {e}")


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

        stats = request.app['counter'].stat.get_stats(period)
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
