from bs4 import BeautifulSoup
from urllib2 import urlopen
import shelve
import re

SEARCH_TERM = 'canon'
CITY = 'stockholm'

def make_soup(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup

def get_item_links():
    soup = make_soup("http://www.blocket.se/" + CITY + "?q=" + SEARCH_TERM)
    items = [item.a["href"] for item in soup.findAll("article", class_ = re.compile("item_row"))]
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

with open("searchoptions.txt") as file:
    for line in file:
        options = line.split(";")
        CITY = options[0]
        SEARCH_TERM = options[1]
        parse_page()
