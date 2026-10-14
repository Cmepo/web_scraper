import sys, requests, asyncio
from urllib.parse import urlsplit
from crawl import * 
from asyncsetup import AsyncCrawler

WEB_PAGE_URL = "https://learnwebscraping.dev/practice/ecommerce/"
WEB_PAGE_RESOURCE = "https://learnwebscraping.dev/practice/ecommerce/products/ashenfang-longsword-fan-1001/"


""" def get_html(url:str):
    html = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    if html.status_code >= 400:
        html.raise_for_status()
    if "text/html" not in html.headers["Content-Type"]:
        raise Exception("Content-Type not text/html")
    return html.text """


""" def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url

    if urlsplit(base_url).hostname != urlsplit(current_url).hostname:
        return 

    if page_data is None:
        page_data = {}

    norm_current_url = normalize_url(current_url)
    if norm_current_url in page_data:
        return
    
    html_current_url = get_html(current_url)
    print(f"Obtained html from normalized current url: {norm_current_url}")
    page_data[norm_current_url] = extract_page_data(html_current_url, current_url)

    for link in page_data[norm_current_url]["outgoing_links"]:
        crawl_page(base_url,link, page_data) """


async def crawl_site_async(BASE_URL):
    base_url = BASE_URL
    base_domain = urlsplit(base_url).hostname
    page_data = {}
    visited = set()
    max_concurrency = 5
    args = [base_url, base_domain, page_data, visited, max_concurrency]
    async with AsyncCrawler(*args) as crawler:
        return await crawler.crawl()
        
async def main():
    print("Hello from web-scraper!")

    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)

    script_name = sys.argv[0]
    base_url = sys.argv[1]

    print(f"starting crawl of: {base_url}.. .")
    #crawl_page(BASE_URL, page_data=data)
    page_data = await crawl_site_async(base_url)

    print(f"Pages found: {len(page_data)}")
    for page in page_data.values():
        print(page)

if __name__ == "__main__":
    asyncio.run(main())
