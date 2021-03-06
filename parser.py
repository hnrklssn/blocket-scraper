from bs4 import BeautifulSoup
from urllib2 import urlopen
import shelve
import re
import sys
from pushbullet import Pushbullet

SEARCH_TERM = 'canon'
CITY = 'stockholm'
CATEGORY = '0'
MIN_PRICE_DEFAULT = -1
MAX_PRICE_DEFAULT = sys.maxint
MIN_PRICE = MIN_PRICE_DEFAULT
MAX_PRICE = MAX_PRICE_DEFAULT
PB_ACTIVE = False
API_KEY = ""

def make_soup(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup

def get_items():
    soup = make_soup("http://www.blocket.se/" + CITY + "?q=" + SEARCH_TERM + "&cg=" + CATEGORY)
    objects = [obj for obj in soup.findAll("article", class_ = re.compile("item_row"))]
    items = []
    for obj in objects:
        item = get_item_details(obj)
        if item["price"] >= MIN_PRICE and item["price"] <= MAX_PRICE:
            items.append(item)
    return items

def price_change(item, old_price):
    print "Price change! " + item["title"] + " Old price: " + old_price + " New price: " + item["price"] + " URL: " + item["url"]
    if PB_ACTIVE:
        pb = Pushbullet(API_KEY)
        pb.push_link("Price changed from " + str(old_price) + ":- to " + str(item["price"]) + ":- | " + item["title"], item["url"])

def get_item_details(obj):
    a = obj.h1.a
    url = a["href"]
    title = unicode(a.string)
    prices = obj.p.contents
    try:
        price_string = prices[0]
        price = int(re.sub("\D", "", price_string)) #removes non-digits and converts to int
    except:
        price = -1
    if len(prices) == 2:
        soup = make_soup(url)
        price_container = soup.find("div", id = "price_container")
        try:
            old_price_string = price_container.find("span", class_ = "text-secondary").s.string
            old_price = int(re.sub("\D", "", old_price_string))
        except:
            old_price = -1
    else: old_price = -1
    return {"url": url, "price": price, "old_price": old_price, "title": title}

def get_new_items(items):
    sh = shelve.open('urlshelve', writeback=True)
    new_items = []
    try:
        urls = sh['urls']
    except:
        urls = sh['urls'] = {}
    for item in items:
        if not item["url"] in urls.iterkeys():
            sh['urls'][item['url']] = item
            new_items.append(item)
            print item
        else:
            price = item["price"]
            old_price = item["old_price"]
            if old_price != -1 and old_price != price:
                last_logged_price = sh['urls'][item['url']]["price"]
                dif = last_logged_price - item["price"]
                if dif >= 100 and dif * 1.0 / last_logged_price >= 0.1 :
                    price_change(item, min(last_logged_price, old_price))
    sh.close()
    return new_items

def parse_page():
    items = get_items()
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

def push_item(items):
    pb = Pushbullet(API_KEY)
    for item in items:
        if item["price"] == -1:
            price_info = "No price: "
        else:
            price_info = str(item["price"]) + ":- | "
        push = pb.push_link(price_info + item["title"], item["url"])

categories = get_categories()

try:
    with open("api_key.txt") as pb_api:
        API_KEY = pb_api.read().rstrip()
        if len(API_KEY) > 25:
            PB_ACTIVE = True
except:
    raise

with open("searchoptions.txt") as file:
    for line in file:
        options = line.rstrip().split(";")
        CITY = options[0]
         #converts category string to category number
        CATEGORY = categories[options[1].lower()]
        SEARCH_TERM = options[2]
        try:
            MIN_PRICE = int(options[3])
        except:
            MIN_PRICE = MIN_PRICE_DEFAULT
        try:
            MAX_PRICE = int(options[4])
        except:
            MAX_PRICE = MAX_PRICE_DEFAULT
        item_list = parse_page()

        if PB_ACTIVE:
            push_item(item_list)
