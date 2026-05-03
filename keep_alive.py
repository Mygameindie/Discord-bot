import os
from aiohttp import web


async def home(request):
    return web.Response(text="Gemini Discord bot is running.")


async def start_keep_alive_server():
    port = int(os.getenv("PORT", "10000"))

    app = web.Application()
    app.router.add_get("/", home)
    app.router.add_get("/health", home)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Keep-alive web server running on port {port}")
