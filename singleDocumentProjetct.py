from bs4 import BeautifulSoup
import aiohttp, asyncio, json

import sqlite3
import redis

# o objetivo é criar um código excelente sem precisar criar arquivos externos

class JournalSpy:
    async def process_response(content: list) -> list:
        # retorna content_pack com todas as notícias processadas e padronizadas: 
        # (
        #    nome do site, 
        #       [
        #         (titulo da news, url da news, descrição da news),
        #         (titulo da news, url da news, descrição da news)
        #       ]
        # )
        
        content_pack = [] 

        for data in content:
            _temp = []

            if data[0] == "g1_news":
                # navega pelo JSON da API DO G1, coleta os dados mais relevantes

                website_name = data[0]
                json_data = json.loads(data[1])

                for news in json_data['items']:
                    try:
                        for posts in news['aggregatedPosts']:
                            content = posts['content']

                            _temp.append((
                                content['title'].strip(),
                                content.get('summary', 'No Summary.'),
                                content['url'].strip()

                            )) # TÍTULO | DESCRIÇÃO | URL DA NOTÍCIA 

                    except KeyError:
                            content = news['content']

                            _temp.append((
                                content['title'].strip(),
                                content.get('summary', 'No Summary.'),
                                content['url'].strip()

                            )) # TÍTULO | DESCRIÇÃO | URL DA NOTÍCIA
            
                content_pack.append((website_name, _temp)) # WEBSITE | LISTA FILTRADA COM MATÉRIAS
            
        return content_pack 

    async def request_layer(url: list) -> list:
        response_pack = []

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as requests:
            for i in url:
                response = await requests.get(url=i[1])
            
                if response.status == 200:
                    response_pack.append((i[0], await response.text())) # WEBSITE | CONTEÚDO

        return response_pack
    

class sqlDatabase:
    def __init__(self):
        self.db_name = ":memory:"
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def storeNews(self, news):
        for block in news:
            table_name = block[0]
        
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} (título TEXT, resumo TEXT, url TEXT UNIQUE)"
            )

            for news in block[1]:
                self.cursor.execute(
                    f"INSERT OR IGNORE INTO {table_name} VALUES (?, ?, ?)", 
                    (news[0], news[1], news[2])
                )
        
    def __enter__(self):
        return self
    
    def __exit__(self, a, b, c):
        self.connection.commit()
        self.connection.close()


url = [["g1_news", "https://falkor-cda.bastian.globo.com/tenants/g1/instances/4af56893-1f9a-4504-9531-74458e481f91/posts/page/1"]]
        
loop = asyncio.new_event_loop()
brutedata = loop.run_until_complete(JournalSpy.request_layer(url=url))
cleanData = loop.run_until_complete(JournalSpy.process_response(content=brutedata))

with sqlDatabase() as db:
    #db.storeNews(news=[("g1", [("choco", "cholate novo", "http://chocolate_branco.com")])])
    db.storeNews(news=cleanData)

