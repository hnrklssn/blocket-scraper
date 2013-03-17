from bs4 import BeautifulSoup
from urllib2 import urlopen

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

def parse_page():
    items = get_item_links()
    print items

parse_page()