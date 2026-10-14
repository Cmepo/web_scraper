import sys, requests

WEB_PAGE_URL = "https://learnwebscraping.dev/practice/ecommerce/"
WEB_PAGE_RESOURCE = "https://learnwebscraping.dev/practice/ecommerce/products/ashenfang-longsword-fan-1001/"


def get_html(url:str):
    html = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    if html.status_code >= 400:
        html.raise_for_status()
    if "text/html" not in html.headers["Content-Type"]:
        raise Exception("Content-Type not text/html")
    return html.text

def main():
    print("Hello from web-scraper!")

    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)

    SCRIPT_NAME = sys.argv[0]
    BASE_URL = sys.argv[1]

    print(f"starting crawl of: {BASE_URL}...")
    html = get_html(BASE_URL)
    print(html)

if __name__ == "__main__":
    main()
