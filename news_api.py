from plugins import pluggin_news_from_g1, pluggin_news_from_nyt
from playwright.async_api import async_playwright

import aiohttp, asyncio
import sqlite3

class JournalSpy:
    @staticmethod
    async def process_response(content: list) -> list:        
        content_pack = [] 

        for website_name, raw in content:
            if website_name == "g1_news":
                results = pluggin_news_from_g1.g1.process_response(raw=raw)
                content_pack.append((website_name, results))

            elif website_name == "new_york_times":
                results = await pluggin_news_from_nyt.New_York_Times.process_response(raw=raw)
                content_pack.append((website_name, results))

        return content_pack

    @staticmethod
    async def request_layer(url: list) -> list:
        response_pack = []
        complex_headers = headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.9"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Ch-Ua": (
                '"Chromium";v="124", "Not-A.Brand";v="99", "Google Chrome";v="124"'
            ),
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

        for_rendering_page_list = ["new_york_times"]

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as requests:
            for website_name, website_url in url:

                if website_name in for_rendering_page_list:
                    async with async_playwright() as driver:
                        browser = await driver.chromium.launch(headless=False)
                        page = await browser.new_page()
                        await page.goto(website_url)
                        await page.wait_for_load_state('networkidle')
                        response_pack.append((website_name, await page.inner_html("main")))

                else:

                    response = await requests.get(url=website_url, headers=complex_headers)
                
                    if response.status == 200:
                        response_pack.append((website_name, await response.text()))

        return response_pack
    

class sqlDatabase:
    def __init__(self, db_name=":memory:"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def storeNews(self, news):
        for table_name, entries in news:
        
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, título TEXT NOT NULL, resumo TEXT, url TEXT UNIQUE NOT NULL)"
            )
       
            self.cursor.executemany(
                f"INSERT OR IGNORE INTO {table_name} (título, resumo, url) VALUES (?, ?, ?)", 
                entries
            )
        
    def __enter__(self):
        return self
    
    def __exit__(self, a, b, c):
        self.connection.commit()
        self.connection.close()

# ==========================

if __name__ == "__main__":

    url = [
            #("g1_news", "https://falkor-cda.bastian.globo.com/tenants/g1/instances/4af56893-1f9a-4504-9531-74458e481f91/posts/page/1"),
            ("new_york_times", "https://www.nytimes.com/")
        ]
            
    loop = asyncio.new_event_loop()
    brutedata = loop.run_until_complete(JournalSpy.request_layer(url=url))
    cleanData = loop.run_until_complete(JournalSpy.process_response(content=brutedata))

    with sqlDatabase() as db:
        #db.storeNews(news=[("g1", [("choco", "cholate novo", "http://chocolate_branco.com")])])
        db.storeNews(news=cleanData)
    
    print(cleanData)
