import requests
from scrapy import Selector
import pandas as pd

# basic conf...........
base_url = "https://wornontv.net"
url = base_url + "/shows/"

# request the url.......
r = requests.get(url)

if r.status_code == 200:

    # get links where product links available with pages......
    links = Selector(text=r.text).xpath('//div[@id="fullshowlist"]//ul//li/a').xpath('@href').extract()

    # get detail of data......
    for li in links:

        show_name = li.replace("/", '')

        # create link....
        show_link = base_url + li

        # request for links.....
        product_listing = requests.get(show_link)
        if product_listing.status_code == 200:

            # total product link for show....
            product_list = []
            print("On show {}".format(show_name))

            # get max page no............
            total_page = Selector(text=product_listing.text).xpath(
                '//ol[@class="wp-paginate font-inherit"]//li//a').xpath('@title').extract()

            # get links of current show in product_list......
            if len(total_page) > 0:
                for p in range(2, int(total_page[-1]) + 1):
                    page_prodict_data = requests.get(show_link + "page/" + str(p) + "/")
                    if page_prodict_data.status_code == 200:
                        pxpath = Selector(text=product_listing.text).xpath(
                            '//div[@id="grid"]//div[@class="loop apost"]//a').xpath('@href').extract()
                        if pxpath:
                            product_list = product_list + pxpath
            pxpath = Selector(text=product_listing.text).xpath('//div[@id="grid"]//div[@class="loop apost"]//a').xpath(
                '@href').extract()
            if pxpath:
                product_list = product_list + pxpath
            for product_link in product_list:
                product_detail_req = requests.get(product_link)
                if product_detail_req.status_code == 200:

                    product_info2 = Selector(text=product_detail_req.text).xpath(
                        '//div[@id="single-inner"]//text()').extract()
                    product_info2 = [x.replace('\t', '').replace('\n', '') for x in product_info2]
                    product_info2 = [" ".join(x.split()) for x in product_info2]
                    product_info2 = [xs for xs in product_info2 if xs]

                    product_info = Selector(text=product_detail_req.text).xpath(
                        '//div[@class="metabox"]//text()').extract()
                    product_info = [x.replace('\t', '').replace('\n', '') for x in product_info]
                    product_info = [" ".join(x.split()) for x in product_info]
                    product_info = [xs for xs in product_info if xs]


                    try:
                        worn_on = " ".join([product_info[product_info.index(wo) + 1:product_info.index('Worn by:')]
                                        for wo in product_info if "Worn on:" in wo][0])
                    except Exception:
                        worn_on = ''
                    try:
                        worn_by = " ".join([product_info[product_info.index(wo) + 1:product_info.index('Posted on:')]
                                        for wo in product_info if "Worn by:" in wo][0])
                    except Exception:
                        worn_by = ''
                    try:
                        posted_on = " ".join([
                        product_info[product_info.index(wo) + 1:product_info.index('Posted by:')]
                        for wo in product_info if "Posted on:" in wo][0])
                    except Exception:
                        posted_on = ''
                    try:
                        posted_by = " ".join([
                        product_info[product_info.index(wo) + 1:product_info.index('Tags:')]
                        for wo in product_info if "Posted by:" in wo][0])
                    except Exception:
                        posted_by= ''
                    try:
                        tags = " ".join([
                        product_info[product_info.index(wo) + 1:]
                        for wo in product_info if "Tags:" in wo][0])
                    except Exception:
                        tags = ''

                    print("Completed link no. {} from total of {}".format(product_list.index(product_link)+1,len(product_list)))
            print("Get all detail of show {}".format(show_name))

        else:
            print("Have some issues with the page.")
else:
    print("Have some issues with the site.")
