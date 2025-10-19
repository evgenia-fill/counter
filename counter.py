from aiohttp import web
from datetime import datetime
from data import Data
from statistics import Statistics
import aiohttp


class VisitCounter:
    def __init__(self, storage_file='visits.json'):
        self.storage_file = storage_file
        self.data = Data(storage_file)
        self.stat = Statistics(self.data)

    async def get_region_from_ip(self, ip):
        if ip.startswith("127.") or ip.startswith("::1"):
            return "Localhost"
        url = f"https://ipwho.is/{ip}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=3) as resp:
                    data = await resp.json()
                    if data.get("success"):
                        return data.get("country", "Unknown")
        except Exception:
            pass
        return "Unknown"

    def add_visit(self, visitor_id, region="Unknown"):
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

        self.data['by_region'][region] += 1
        self.data['unique_by_region'][region].add(visitor_id)

        self.data.save()

    def get_stats(self, period='total'):
        return self.stat.get_stats(period)


async def visit_handler(request):
    visitor_ip = request.remote or "127.0.0.1"
    region = await request.app['counter'].get_region_from_ip(visitor_ip)
    request.app['counter'].add_visit(visitor_ip, region)
    stats = request.app['counter'].get_stats('total')
    content = f"""
    <div class="stats">
        <p><strong>Ваш IP:</strong> {visitor_ip}</p>
        <p><strong>Страна:</strong> {region}</p>
        <p><strong>Общее количество посещений:</strong> {stats['total']}</p>
        <p><strong>Уникальных посетителей:</strong> {stats['unique']}</p>
    </div>
    <p>+Новое посещение! ✅</p>
    """
    return web.Response(text=html_page("Новое посещение", content), content_type='text/html')


def html_page(title, content):
    return f"""
    <html>
        <head>
            <title>{title}</title>
             <meta charset="utf-8">
             <style>
                body {{ font-family: Arial, sans-serif; 40px; background: #fafafa; }}
                h1 {{ color: #333; }}
                .stats, .table-wrapper {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ padding: 8px 12px; border-bottom: 1px solid #ddd; text-align: left; }} th {{ background: #007bff; color: #fff; }} tr:hover {{ background: #f1f1f1; }}
                a {{ color: #007bff; text-decoration: none; margin-right: 10px; }} 
                a:hover {{ text-decoration: underline; }}
                footer {{ margin-top: 40px; font-size: 0.9em; color: #888; }}
             </style>
        </head>
        <body>
            <h1>📊 Счетчик посещений</h1>
            <div>{content}</div>
            <footer>
                <p>
                    <a href="/">🏠 Главная</a>
                    <a href="/visit">➕ Добавить посещение</a>
                    <a href="/stats">📈 Статистика (общая)</a>
                    <a href="/stats?period=daily">📅 По дням</a>
                    <a href="/stats?period=monthly">🗓 По месяцам</a>
                    <a href="/stats?period=yearly">📆 По годам</a>
                    <a href="/stats?period=regionally">🗺️ По странам/регионам</a>
                </p>
            </footer>
        </body>
    </html>
    """


async def stats_handler(request):
    try:
        period = request.query.get('period', 'total')
        output_format = request.query.get('format', 'html')
        if period not in ['total', 'yearly', 'monthly', 'daily', 'regionally']:
            return web.json_response({'error': 'Invalid period. Use: total, yearly, monthly, daily'}, status=400)

        stats = request.app['counter'].get_stats(period)
        if output_format == 'json':
            return web.json_response(stats)
        if period == 'total':
            content = f"""
            <div class="stats"> 
                <p><strong>Всего посещений:</strong> {stats['total']}</p>
                <p><strong>Уникальных посетителей:</strong> {stats['unique']}</p>
            <div/>
            """
        elif period == 'regionally':
            rows = "".join(
                f"<tr><td>{k}</td><td>{v['total']}</td><td>{v['unique']}</td></tr>"
                for k, v in sorted(stats.items())
            )
            content = f"""
            <div class="table-wrapper">
                <h2>Статистика по странам</h2>
                <table>
                    <tr><th>Страна</th><th>Всего</th><th>Уникальных</th></tr>
                    {rows}
                </table>
            </div>
            """
        else:
            rows = "".join(
                f"<tr><td>{k}</td><td>{v['total']}</td><td>{v['unique']}</td></tr>"
                for k, v in sorted(stats.items()))

            content = f"""
                        <div class="table-wrapper">
                            <h2>Статистика ({period})</h2>
                            <table>
                                <tr><th>Период</th><th>Всего</th><th>Уникальных</th></tr>
                                {rows}
                            </table>
                        </div>"""

        return web.Response(text=html_page(f"Статистика ({period})", content), content_type='text/html')
    except Exception as e:
        return web.Response(text=html_page("Ошибка", f"<p>Ошибка: {e}</p>"), content_type='text/html', status=500)


async def favicon_handler(request):
    return web.Response(status=404)


async def not_found_handler(request):
    return web.Response(text=html_page("404", "<p>Страница не найдена 😢</p>"), content_type='text/html', status=404)


async def index_handler(request):
    stats = request.app['counter'].get_stats('total')
    content = f"""
    <div class="stats">
        <p><strong>Всего посещений:</strong> {stats['total']}</p>
        <p><strong>Уникальных посетителей:</strong> {stats['unique']}</p>
    </div>
    <p>Выберите действие ниже:</p>
    <ul>
        <li><a href="/visit">➕ Добавить посещение</a></li>
        <li><a href="/stats">📈 Подробная статистика</a></li>
        <li><a href="/stats?period=daily">📅 По дням</a></li>
        <li><a href="/stats?period=monthly">🗓 По месяцам</a></li>
        <li><a href="/stats?period=yearly">📆 По годам</a></li>
        <li><a href="/stats?period=regionally">️🗺 По странам/регионам</a></li>
    </ul>
    """
    return web.Response(text=html_page("Главная", content), content_type='text/html')


async def init_app():
    app = web.Application()
    app['counter'] = VisitCounter()

    app.router.add_get('/', index_handler)
    app.router.add_get('/visit', visit_handler)
    app.router.add_get('/stats', stats_handler)
    app.router.add_get('/favicon.ico', favicon_handler)
    app.router.add_get('/{tail:.*}', not_found_handler)

    return app


if __name__ == '__main__':
    print("   http://localhost:8085/ - Главная страница")
    print("   http://localhost:8085/visit - Добавить посещение")
    print("   http://localhost:8085/stats - Статистика")
    print("   http://localhost:8085/stats?period=daily - Статистика по дням")
    print("   http://localhost:8085/stats?period=monthly - Статистика по месяцам")
    print("   http://localhost:8085/stats?period=yearly - Статистика по годам")
    print("   http://localhost:8085/stats?period=regionally - Статистика по странам/регионам")
    web.run_app(init_app(), host='localhost', port=8085)
