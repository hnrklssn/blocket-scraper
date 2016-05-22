from bs4 import BeautifulSoup
from urllib2 import urlopen
import shelve
import re

SEARCH_TERM = 'canon'
CITY = 'stockholm'
CATEGORY = '0'

def make_soup(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup

def get_item_links():
    soup = make_soup("http://www.blocket.se/" + CITY + "?q=" + SEARCH_TERM + "&cg=" + CATEGORY)
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
    return new_items

def get_categories():
    soup = make_soup("http://www.blocket.se/hela_sverige?")
    items = soup.find_all("option", class_ = True)
    cats = {}
    for item in items:
        if item["class"] != ["blind"]:
            cats[unicode(item.string).lower()] = item["value"]
    return cats

categories = get_categories()

with open("searchoptions.txt") as file:
    for line in file:
        options = line.rstrip().split(";")
        CITY = options[0]
         #converts category string to category number
        CATEGORY = categories[options[1].lower()]
        SEARCH_TERM = options[2]
        parse_page()
