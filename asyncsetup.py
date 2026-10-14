import asyncio, aiohttp
from urllib.parse import urlsplit
from crawl import *

class AsyncCrawler():
    def __init__(self, base_url, base_domain, page_data, visited, max_concurrency) -> None:
        self.base_url = base_url
        self.base_domain = base_domain
        self.page_data = page_data
        self.visited = visited
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if normalized_url in self.visited:
                return False
            else:
                self.visited.add(normalized_url)
                return True

    async def get_html(self, url:str):
        async with self.session.get(url) as response:
            #html = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
            if response.status >= 400:
                response.raise_for_status()
            if "text/html" not in response.headers.get("Content-Type",""):
                raise Exception("Content-Type not text/html")
            return await response.text()

    async def crawl_page(self, current_url=None):
        if current_url is None:
            current_url = self.base_url

        if self.base_domain!= urlsplit(current_url).hostname:
            return 

        norm_current_url = normalize_url(current_url)
        if not await self.add_page_visit(norm_current_url):
            return 

        async with self.semaphore:
            html_current_url = await self.get_html(current_url)
            print(f"Obtained html from normalized current url: {norm_current_url}")
            async with self.lock:
                self.page_data[norm_current_url] = extract_page_data(html_current_url, current_url)

        tasks = set()
        for link in self.page_data[norm_current_url]["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(link))
            tasks.add(task)

        await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page()
        return self.page_data