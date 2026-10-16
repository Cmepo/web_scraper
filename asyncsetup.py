import asyncio, aiohttp
from urllib.parse import urlsplit
from crawl import *

class AsyncCrawler():
    def __init__(self, base_url, base_domain, page_data, visited, max_concurrency, max_pages) -> None:
        self.base_url = base_url
        self.base_domain = base_domain
        self.page_data = page_data
        self.visited = visited
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = []


    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        assert self.session is not None
        await self.session.close()

    async def add_page_visit(self, normalized_url):

        if self.should_stop:
            return False

        async with self.lock:

            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl")
                return False
            if normalized_url in self.visited:
                return False
            else:
                self.visited.add(normalized_url)            
                return True


        
    async def get_html(self, url:str):
        assert self.session is not None
        async with self.session.get(url,headers={"User-Agent": "BootCrawler/1.0"}) as response:
            #html = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
            if response.status >= 400:
                response.raise_for_status()
            if "text/html" not in response.headers.get("Content-Type",""):
                print("Content-Type not text/html")
                return None
            return await response.text()

    async def crawl_page(self, current_url=None):

        if self.should_stop:
            return 
        
        if current_url is None:
            current_url = self.base_url

        if self.base_domain!= urlsplit(current_url).hostname:
            return 

        norm_current_url = normalize_url(current_url)
        if not await self.add_page_visit(norm_current_url):
            return 

        async with self.semaphore:
            try:
                html_current_url = await self.get_html(current_url)
                if html_current_url:
                    print(f"Obtained html from normalized current url: {norm_current_url}")
                    async with self.lock:
                        self.page_data[norm_current_url] = extract_page_data(html_current_url, current_url)
                else:
                    return
            except aiohttp.ClientResponseError as e:
                print(f"Error {e} fetching html {current_url}")
                return 

        tasks = set()
        for link in self.page_data[norm_current_url]["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(link))
            tasks.add(task)

        await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page()
        return self.page_data