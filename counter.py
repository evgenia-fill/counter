from aiohttp import web

visit_count = 0

async def handle(request):
    global visit_count
    visit_count += 1
    return web.Response(text=f'Hello World! Visit count: {visit_count}')

app = web.Application()
app.router.add_get('/', handle)

if __name__ == '__main__':
    web.run_app(app, port=8080)