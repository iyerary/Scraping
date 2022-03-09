import json

import requests
from scrapy import Selector

for i in range(382):
    if i != 0:
        print("Current page is {}".format(i))
        url = "https://www.charmboard.com/?page={}&api=true".format(i)
        rp = requests.get(url)
        if rp.status_code == 200:
            product_data = ["https://www.charmboard.com"+p["charm_page_url"] for p in json.loads(rp.json()["charm_list"])]
            for product_link in product_data:
                pr = requests.get(product_link)
                title = [x for x in Selector(text=pr.text).xpath('//div[@class="charm-card-tittle common-text-wrap-hide"]//text()').extract() if x]
                print(title)