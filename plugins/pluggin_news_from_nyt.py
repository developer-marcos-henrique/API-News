from bs4 import BeautifulSoup


class New_York_Times:
    @staticmethod
    async def process_response(raw) -> list:
        html = BeautifulSoup(raw[1], "html.parser")
        results = []
        exit()



