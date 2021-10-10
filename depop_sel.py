import datetime
import time
import urllib.request

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome


def depop_item(item, found_items):
    url = item.find('a')['href']
    if url in found_items.keys():
        previously_found = found_items['url']
        previously_found['last_scrape'] = datetime.datetime.now()
        return False
    try:

        description = url.split('products/')[1].replace('-', " ").replace('/', '')
        currency_price = item.contents[1].text
        currency = currency_price[0]
        price = currency_price.split(currency)[1]
        img_src = item.find('img')['src']

        urllib.request.urlretrieve(img_src,
                                   'C:/Users/Tom.Dyson/side_repos/vintage/data/pictures/' + url.replace('/', '_') + '.jpg')


        return {'url': url, 'description': description, 'currency_price': currency_price,
                    'price': float(price), 'first_scrape': datetime.datetime.now(), 'last_scrape': datetime.datetime.now(),
                    'picture_url': url.replace(' / ', '_')}
    except Exception as e:
        return False


def depop_search(browser, search_term, current_items):
    browser.get(f'https://www.depop.com/search/?q={search_term.replace(" ", "%20")}')

    last_height = browser.execute_script("return document.body.scrollHeight")
    found_items = current_items.copy()
    scroll_attempts = 0
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(0.5)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            scroll_attempts += 1
            if scroll_attempts == 3:
                html = browser.page_source
                soup = BeautifulSoup(html)
                current_items = soup.find_all('li', attrs={'class': "styles__ProductCardContainer-sc-__sc-13q41bc-7 cQXZpt"})
                for item in current_items:
                    item_dict = depop_item(item, found_items)
                    if item_dict:
                        found_items[item_dict['url']] = item_dict

                print(len(found_items))
                # pd.DataFrame(found_items).T.to_csv('current_depop_hoody.csv')
                break
        else:
            scroll_attempts = 0
        last_height = new_height
    return found_items


browser = Chrome(executable_path='C:/Users/Tom.Dyson/chromedriver.exe')
depop_items = {}

search_terms = ['small mens sweatshirt']#, 'medium mens sweatshirt', 'large mens sweatshirt']

for search_term in search_terms:
    found_depop = depop_search(browser, search_term, depop_items)
    for key, value in found_depop.items():
        depop_items[key] = value

pd.DataFrame(depop_items).T.to_csv('../depop.csv')
