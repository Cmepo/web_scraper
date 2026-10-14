from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

class PageData(TypedDict):
    url:str
    heading:str
    first_paragraph:str
    outgoing_links:list[str]
    image_urls:list[str]

def normalize_url(url:str) -> str:
    split = urlsplit(url=url)
    try:
        if split.hostname != None:
            norm_url = split.hostname + split.path.rstrip("/")
            return norm_url
        else:
            raise Exception
    except:
        print("Error normalizing the url")

def get_heading_from_html(html:str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    h_tag = None
    if soup.find("h1") != None:
        h_tag = soup.find("h1")
    elif soup.find("h2") != None:
        h_tag = soup.find("h2") 
    else:
        return ""
    
    return h_tag.get_text().strip() if isinstance(h_tag, Tag) else ""

def get_first_paragraph_from_html(html:str) -> str: 
    soup = BeautifulSoup(html, 'html.parser')
    if soup.main:
        if soup.main.p:
            return soup.main.p.get_text().strip()
    elif soup.p:
        return soup.p.get_text().strip()
    else:
        return ""

def get_urls_from_html(html:str, base_url:str) -> list:
    soup = BeautifulSoup(html, 'html.parser')
    url_list = []
    for a in soup.find_all('a'):
        if not isinstance(a, Tag):
            continue
        href = a.get("href")
        if isinstance(href,str) and href:
            try:
                abs_url = urljoin(base_url,href)
                url_list.append(abs_url)
            except Exception as e:
                print(f"{e}: {href}")
    return url_list

def get_images_from_html(html:str, base_url:str) -> list:
    soup = BeautifulSoup(html, 'html.parser')
    url_list = []
    for img in soup.find_all('img'):
        if not isinstance(img, Tag):
            continue
        src = img.get("src")
        if isinstance(src,str) and src:
            try:
                abs_url = urljoin(base_url, src)
                url_list.append(abs_url)
            except Exception as e:
                print(f"{e}: {src}")
    return url_list

def extract_page_data(html: str, page_url: str):
    norm_url = normalize_url(page_url)
    dictionary:PageData = {
        "url":page_url,
        "heading":get_heading_from_html(html),
        "first_paragraph":get_first_paragraph_from_html(html),
        "outgoing_links":get_urls_from_html(html,page_url),
        "image_urls":get_images_from_html(html,page_url),
    }
    return dictionary





































        


