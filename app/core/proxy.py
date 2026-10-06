import aiohttp
import aiohttp.web
import asyncio
from app.config import TARGET_SERVER, PROXY_PORT, HOST
from app.utils.logger import logger
from app.filters.filters import Rules
from multidict import CIMultiDict

waf_rules = Rules()

#İstemciden gelen HTTP isteklerini karşılar, WAF filtresinden geçirir ve eğer temizse hedef sunucuya asenkron olarak yönlendirir.
async def handle(request):
    path = request.rel_url
    query = request.query_string
    method = request.method
    headers = request.headers
    body = await request.read()

    logger.info(f"Received {method} request for {path}")

    if waf_rules.is_blocked(str(path), body, query):
        logger.warning(f"Request blocked by WAF | Path: {path} | Query: {query}")
        return aiohttp.web.Response(status=403, text="Forbidden: WAF Security Rule Triggered")

    async with aiohttp.ClientSession() as session:
        async with session.request(method, f"{TARGET_SERVER}{path}", headers=headers, data=body) as response:
            response_body = await response.read()
            new_headers = CIMultiDict(response.headers)
            
            logger.info(f"Forwarded {method} {path} | Target Status: {response.status}")
            return aiohttp.web.Response(body=response_body, status=response.status, headers=new_headers)

#Reverse Proxy sunucusunu ve tüm rotaları (başlatır.
async def init_app():
    app = aiohttp.web.Application()
    app.router.add_route('*', '/{tail:.*}', handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    
    site = aiohttp.web.TCPSite(runner, HOST, PROXY_PORT)
    logger.info(f"Starting WAF proxy server on port {PROXY_PORT}")
    await site.start()

    while True:
        await asyncio.sleep(3600)