from bs4 import BeautifulSoup
from urllib2 import urlopen
import shelve

SEARCH_TERM = 'canon'
CITY = 'stockholm'

def make_soup(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup

def get_item_links():
    soup = make_soup("http://www.blocket.se/" + CITY + "?q=" + SEARCH_TERM)
    items = [item.a["href"] for item in soup.findAll("div", { "class" : "item_row" })]
    return items

def get_new_items(items):
    sh = shelve.open('urlshelve', writeback=True)
    new_urls = []
    try:
        urls = sh['urls']
    except:
        urls = sh['urls'] = set()
    for item in items:
        if not item in urls:
            sh['urls'].add(item)
            new_urls.append(item)
            print item
    sh.close()
    return new_urls

def parse_page():
    items = get_item_links()
    new_items = get_new_items(items)


parse_page()