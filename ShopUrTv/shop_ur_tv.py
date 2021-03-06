import argparse
import json
import os
import requests
from scrapy import Selector
import pandas as pd
import random
import logging
import sys

# logs config.......
file_handler = logging.FileHandler(filename='./shopurtv.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', handlers=handlers)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger("shopurtv_logs")

# basic conf...........
base_url = "https://www.shopyourtv.com/tv-shows/"
csv_path = "./Shopurtv.csv"

# Argument config ....
parser = argparse.ArgumentParser()
parser.add_argument('--s', type=str, required=True, help="This is for staring point.")
parser.add_argument('--e', type=str, required=True, help="This is for ending point.")

args = parser.parse_args()
starting_point = int(args.s)
ending_point = int(args.e)


# request the url.......
r = requests.get(base_url)

if r.status_code == 200:

    # get links where product links available with pages......
    links = Selector(text=r.text).xpath('//div[@class="cols"]//li//a').xpath('@href').extract()

    logger.info("Total shows is {}".format(len(links)))

    if links:
        # get detail of data......
        for li in range(starting_point - 1, ending_point):
            show_link = links[li]
            show_name = show_link.split("/")[3]

            # request for links.....
            product_listing = requests.get(show_link)
            if product_listing.status_code == 200:

                # total product link for show....
                product_list = []
                logger.info("On show {}".format(show_name))

                # get max page no............
                total_page = Selector(text=product_listing.text).xpath(
                    '//div[@class="navigation"]//ul//li').extract()

                select_page = Selector(text=product_listing.text).xpath(
                    '(//div[@class="navigation"]//ul//li)[{}]//text()'.format(len(total_page) - 1)).extract()

                if select_page:
                    select_page = [int(select_page[0])]

                # get links of current show in product_list......
                if len(select_page) > 0:
                    for p in range(2, int(select_page[-1]) + 1):
                        page_prodict_data = requests.get(show_link + "page/" + str(p) + "/")
                        if page_prodict_data.status_code == 200:
                            pxpath = Selector(text=page_prodict_data.text).xpath(
                                '//a[@rel="bookmark"]').xpath('@href').extract()
                            if pxpath:
                                product_list = product_list + pxpath
                pxpath = Selector(text=product_listing.text).xpath(
                    '//a[@rel="bookmark"]').xpath(
                    '@href').extract()
                if pxpath:
                    product_list = product_list + pxpath
                product_list = list(set(product_list))
                for product_link in product_list:
                    value_check = pd.read_csv(csv_path)

                    if product_link in value_check['Product_link'].tolist():
                        logger.info("Already have product link {} record, so skip this one.".format(product_link))
                    else:
                        try:
                            product_detail_req = requests.get(product_link)
                            if product_detail_req.status_code == 200:

                                # --------------------------------------------------------------------------------------
                                product_info = Selector(text=product_detail_req.text).xpath(
                                    '(//div[@class="col-md-6"])[2]//text()').extract()
                                product_info = [x.replace('\t', '').replace('\n', '') for x in product_info]
                                product_info = [" ".join(x.split()) for x in product_info]

                                # --------------------------------------------------------------------------------------
                                buy_link_info = Selector(text=product_detail_req.text).xpath(
                                    '(//div[@class="col-md-6"])[2]//li/p//a').xpath('@href').extract()

                                # --------------------------------------------------------------------------------------
                                title_info = Selector(text=product_detail_req.text).xpath(
                                    '//span[@itemprop="name"]//text()').extract()

                                # --------------------------------------------------------------------------------------
                                img_info = Selector(text=product_detail_req.text).xpath(
                                    '(//div[@class="col-md-6"])[1]//img').xpath('@src').extract()

                                # --------------------------------------------------------------------------------------
                                description = get_it_second_hand = celeb_image = title = buy_link = ''

                                # --------------------------------------------------------------------------------------
                                ids = int(str(random.randint(1, 10000000000000000000000000))[:5])
                                actor = [product_info[product_info.index(ac) + 1] for ac in product_info if
                                         "Actor" in ac]
                                show_series_name = [product_info[product_info.index(ac) + 1] for ac in product_info if
                                                    "Show" in ac]
                                episode = [product_info[product_info.index(ac) + 1] for ac in product_info if
                                           "Episode" in ac]
                                brand_product = [product_info[product_info.index(ac) + 1] for ac in product_info if
                                                 "Brand Product" in ac]
                                try:
                                    buy_price = [
                                        product_info[product_info.index(ac) + 1:product_info.index("Description:")] for
                                        ac in product_info if "Buy" in ac]
                                    if buy_price:
                                        buy_price = buy_price[0][1]
                                except Exception:
                                    buy_price = ''
                                get_it_second_hand = [product_info[product_info.index(ac) + 1] for ac in product_info if
                                                      "Get it second hand" in ac]
                                if get_it_second_hand:
                                    get_it_second_hand = get_it_second_hand[0]
                                description = [product_info[product_info.index(ac) + 1] for ac in product_info if
                                               "Description" in ac]
                                if description:
                                    description = description[0]

                                if buy_link_info:
                                    buy_link = buy_link_info[0]

                                if title_info:
                                    title = title_info[-1]

                                if img_info:
                                    celeb_image = img_info[0]

                                fields = [[ids, title, "", product_link, description, brand_product, "", "", "", "",
                                           show_series_name, ""
                                              , "", episode, actor, "", celeb_image, "Mainstream", "", "", "",
                                           buy_price, buy_link, "", "Shopurtv",
                                           "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                                           get_it_second_hand]]

                                new_df = pd.DataFrame(fields,
                                                      columns=['Id', 'Title', 'Short Description', 'Product_link',
                                                               'Description',
                                                               'Product Name',
                                                               'Product Brand', 'Outfit Name', 'Outfit Description',
                                                               'Outfit Image', 'Movie/Show',
                                                               'Series Description',
                                                               'Series No', 'Episode', 'Celebrity Name',
                                                               'Character Name',
                                                               'Celebrity Image', 'Celebrity Type', 'Image1',
                                                               'Image2',
                                                               'Media',
                                                               'Buy', 'Buy Link',
                                                               'Extra_description', 'Source', 'Key works',
                                                               'In House',
                                                               'In House Price',
                                                               'Why we Like it', 'Who will this suit', 'Region',
                                                               'Year',
                                                               'Video',
                                                               'Exact Image', 'Exact Store', 'Exact Price',
                                                               'Exact BuyLink',
                                                               'Similar Image', 'Similar Store', 'Similar Price',
                                                               'Similar BuyLink', 'Get It Second Hand'])
                                new_df.to_csv(csv_path, mode='a', header=False, index=False)

                                logger.info("Completed link no. {} from total of {}".format(
                                    product_list.index(product_link) + 1,
                                    len(product_list)))
                        except Exception as e:
                            with open("./exception_link.txt", 'a+') as fp:
                                fp.write(product_link + "\n")
                            logger.error("Have some issues with the link {}".format(product_link))
                            pass
                logger.info("Get all detail of show {}".format(show_name))

            else:
                logger.info("Have some issues with the page.")
    else:
        logger.info("Have some issues with the site.")


else:
    logger.info("Have some issues with the site.")
