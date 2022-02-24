import argparse
import json
import requests
from scrapy import Selector
import pandas as pd
import random
import logging
import sys

# logs config.......
file_handler = logging.FileHandler(filename='./wornontv.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', handlers=handlers)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger("wornontv_logs")

# basic conf...........
base_url = "https://wornontv.net/"
url = base_url + "shows/"
csv_path = "./Wornontv.csv"
heads = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    "Upgrade-Insecure-Requests": "1", "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate"}

# Argument config ....
parser = argparse.ArgumentParser()
parser.add_argument('--s', type=str, required=True, help="This is for staring point.")
parser.add_argument('--e', type=str, required=True, help="This is for ending point.")

args = parser.parse_args()
starting_point = int(args.s)
ending_point = int(args.e)


# request the url.......
r = requests.get(url)

if r.status_code == 200:

    # get links where product links available with pages......
    links = Selector(text=r.text).xpath('//div[@id="fullshowlist"]//ul//li/a').xpath('@href').extract()

    logger.info("Total shows is {}".format(len(links)))

    if links:
        links = [ln.replace("/", '') for ln in links]

        # get detail of data......
        for li in range(starting_point-1, ending_point):
            show_name = links[li]

            # create link....
            show_link = base_url + show_name + "/"

            # request for links.....
            product_listing = requests.get(show_link)
            if product_listing.status_code == 200:

                # total product link for show....
                product_list = []
                logger.info("On show {}".format(show_name))

                # get max page no............
                total_page = Selector(text=product_listing.text).xpath(
                    '//ol[@class="wp-paginate font-inherit"]//li//a').xpath('@title').extract()

                # get links of current show in product_list......
                if len(total_page) > 0:
                    for p in range(2, int(total_page[-1]) + 1):
                        page_prodict_data = requests.get(show_link + "page/" + str(p) + "/")
                        if page_prodict_data.status_code == 200:
                            pxpath = Selector(text=page_prodict_data.text).xpath(
                                '//div[@id="grid"]//div[@class="loop apost"]//a').xpath('@href').extract()
                            if pxpath:
                                product_list = product_list + pxpath
                pxpath = Selector(text=product_listing.text).xpath(
                    '//div[@id="grid"]//div[@class="loop apost"]//a').xpath(
                    '@href').extract()
                if pxpath:
                    product_list = product_list + pxpath
                product_list = list(set(product_list))
                for product_link in product_list:
                    value_check = pd.read_csv("F:\PycharmProjects\Ascrape\WornOnTv\Wornontv.csv")

                    if product_link in value_check['Product_link'].tolist():
                        logger.info("Already have product link {} record, so skip this one.".format(product_link))
                    else:
                        try:
                            product_detail_req = requests.get(product_link)
                            if product_detail_req.status_code == 200:
                                product_info = Selector(text=product_detail_req.text).xpath(
                                    '//div[@id="single-inner"]//text()').extract()
                                product_info = [x.replace('\t', '').replace('\n', '') for x in product_info]
                                product_info = [" ".join(x.split()) for x in product_info]

                                # detail data...........
                                product_info = [xs for xs in product_info if xs]
                                celeb_episode_detail = json.loads([od for od in product_info if "@context" in od][0])
                                other_desc = json.loads([od for od in product_info if "@context" in od][-1])
                                json_detail = [od for od in product_info if "@context" in od]

                                # fields..........
                                ids = int(str(random.randint(1, 10000000000000000000000000))[:5])
                                title = product_info[0]
                                series_name = celeb_episode_detail["name"]
                                season_number = celeb_episode_detail["partOfSeason"]["seasonNumber"]
                                character = celeb_episode_detail["character"]["name"]
                                actor = celeb_episode_detail["actor"]["name"]
                                episode = celeb_episode_detail["episodeNumber"]
                                try:
                                    tags = other_desc["keywords"]
                                except Exception:
                                    try:
                                        tags = [product_info[product_info.index(od) + 1] for od in product_info if
                                                "Tags" in od]
                                    except Exception:
                                        tags = ""

                                try:
                                    description = other_desc["articleBody"].split("For shoppable links")[0]
                                except Exception:
                                    description = ""
                                images = [im["url"] for im in other_desc["image"]]
                                celeb_image = images[0]

                                exact_similar = Selector(text=product_detail_req.text).xpath(
                                    '//div[@class="products-wrap"]//span[@class="product-store"]//text()').extract()
                                exact_final_xpath = similar_final_xpath = None
                                exact_image = exact_store = exact_price = similar_image = similar_store = similar_price = similar_buy_link = exact_buy_link = [
                                    '']
                                for es in exact_similar:
                                    exact_paths = '//div[@class="product-item  product-{}"]//img[@class="exact-match "]'.format(
                                        es)
                                    similar_paths = '//div[@class="product-item  product-{}"]//img[@class="similar-match "]'.format(
                                        es)
                                    tester1 = Selector(text=product_detail_req.text).xpath(exact_paths).extract()
                                    if tester1:
                                        exact_final_xpath = '//div[@class="product-item  product-{}"]'.format(es)
                                    tester2 = Selector(text=product_detail_req.text).xpath(similar_paths).extract()
                                    if tester2:
                                        similar_final_xpath = '//div[@class="product-item  product-{}"]'.format(es)


                                def exact_sim_buy_link(es_xpath):

                                    es_image = Selector(text=product_detail_req.text).xpath(es_xpath
                                                                                            + '//span[@class="product-item-image "]//img').xpath(
                                        "@src").extract()
                                    if es_image:
                                        es_image = [base_url + es_image[0]]
                                    es_store = Selector(text=product_detail_req.text).xpath(
                                        es_xpath + '//span[@class="product-store"]//text()').extract()
                                    es_price = Selector(text=product_detail_req.text).xpath(
                                        es_xpath + '//span[@class="product-price"]//text()').extract()
                                    es_buy_link_of_worn_on = Selector(text=product_detail_req.text).xpath(
                                        es_xpath + '//a').xpath("@href").extract()

                                    link_req = requests.get(es_buy_link_of_worn_on[0], headers=heads)
                                    xsdc = link_req.text
                                    buy_encode = Selector(text=link_req.text).xpath(
                                        '//meta[@http-equiv="refresh"]').xpath(
                                        '@content').extract()
                                    if es_store[0].lower() == "amazon":
                                        buy_encode = Selector(text=link_req.text).xpath(
                                            '//link[@rel="canonical"]').xpath(
                                            '@href').extract()
                                    elif es_store[0].lower() == "farfetch":
                                        buy_encode = [
                                            Selector(text=link_req.text).xpath('//meta[@http-equiv="refresh"]').xpath(
                                                '@content').extract()[0].split(":")[-1]]
                                    elif es_store[0].lower() == "saks fifth avenue":
                                        try:
                                            buy_encode = \
                                                Selector(text=link_req.text).xpath('//wainclude').xpath(
                                                    '@url').extract()[
                                                    0].split(
                                                    "pid=")[-1]
                                            buy_encode = [
                                                "https://www.saksfifthavenue.com/product/show?pid=" + buy_encode]
                                        except Exception:
                                            pass
                                    if buy_encode:
                                        buy_link = [
                                            buy_encode[0].split("murl=")[-1].split("&")[0].replace("%2F", "/").replace(
                                                "%3F", "?").replace("%3D", "=").replace(" %26", "&").replace("%3A",
                                                                                                             ":")]
                                    else:
                                        buy_link = [""]
                                    return es_image, es_store, es_price, buy_link


                                if exact_final_xpath:
                                    exact_image, exact_store, exact_price, exact_buy_link = exact_sim_buy_link(
                                        exact_final_xpath)
                                if similar_final_xpath:
                                    similar_image, similar_store, similar_price, similar_buy_link = exact_sim_buy_link(
                                        similar_final_xpath)

                                exact = {"image": exact_image[0], "store": exact_store[0], "price": exact_price[0],
                                         "buy_link": exact_buy_link[0]}
                                similar = {"image": similar_image[0], "store": similar_store[0],
                                           "price": similar_price[0], "buy_link": similar_buy_link[0]}


                                def csv_data_save(on, od, oi):
                                    fields = [
                                        [ids, "", product_link, description, title, "", on, od, oi, show_name,
                                         series_name,
                                         season_number, episode, actor, character, celeb_image, "Mainstream", ""
                                            , "", "", "", "", "WornOnTv", tags, "", "", "", "", "", "", "",
                                         exact_image[0],
                                         exact_store[0],
                                         exact_price[0], exact_buy_link[0], similar_image[0], similar_store[0],
                                         similar_price[0], similar_buy_link[0]
                                         ]]

                                    new_df = pd.DataFrame(fields,
                                                          columns=['Id', 'Short Description', 'Product_link',
                                                                   'Description',
                                                                   'Product Name',
                                                                   'Product Brand', 'Outfit Name', 'Outfit Description',
                                                                   'Outfit Image', 'Movie/Show',
                                                                   'Series name',
                                                                   'Series No', 'Episode', 'Celebrity Name',
                                                                   'Character Name',
                                                                   'Celebrity Image', 'Celebrity Type', 'Image1',
                                                                   'Image2',
                                                                   'Media',
                                                                   'Buy',
                                                                   'Extra_description', 'Source', 'Key works',
                                                                   'In House',
                                                                   'In House Price',
                                                                   'Why we Like it', 'Who will this suit', 'Region',
                                                                   'Year',
                                                                   'Video',
                                                                   'Exact Image', 'Exact Store', 'Exact Price',
                                                                   'Exact BuyLink',
                                                                   'Similar Image', 'Similar Store', 'Similar Price',
                                                                   'Similar BuyLink'])
                                    new_df.to_csv(csv_path, mode='a', header=False, index=False)

                                    logger.info("Completed link no. {} from total of {}".format(
                                        product_list.index(product_link) + 1,
                                        len(product_list)))


                                outfit_details = \
                                    [product_info[product_info.index("Outfit Details") + 1:product_info.index(od)] for
                                     od in
                                     product_info if "@context" in od][0]
                                ods = [ij for ij in outfit_details if ":" in ij]
                                if ods:
                                    for kj in ods:
                                        try:
                                            end_range = outfit_details.index(ods[ods.index(kj) + 1])
                                            outfit_desc = " ".join(
                                                outfit_details[outfit_details.index(kj) + 1:end_range])
                                        except Exception:
                                            outfit_desc = " ".join(outfit_details[outfit_details.index(kj) + 1:])
                                        try:
                                            image_outfit = images[ods.index(kj) + 1]
                                        except Exception:
                                            image_outfit = Selector(text=product_detail_req.text).xpath(
                                                '//div[@class="figure-image"]//img').xpath("@src").extract()
                                            if image_outfit:
                                                image_outfit = image_outfit[0]
                                            else:
                                                image_outfit = ''
                                        csv_data_save(kj.replace(":", ""), outfit_desc, image_outfit)
                                else:
                                    csv_data_save("", "", "")
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
