import json
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
                    product_info = Selector(text=product_detail_req.text).xpath(
                        '//div[@id="single-inner"]//text()').extract()
                    product_info = [x.replace('\t', '').replace('\n', '') for x in product_info]
                    product_info = [" ".join(x.split()) for x in product_info]
                    product_info = [xs for xs in product_info if xs]

                    celeb_episode_detail = json.loads([od for od in product_info if "@context" in od][0])
                    other_desc = json.loads([od for od in product_info if "@context" in od][-1])

                    title = product_info[0]
                    outfit_details = " ".join([product_info[product_info.index("Outfit Details") + 1:product_info.index(od)] for od in
                     product_info if "@context" in od][0])
                    series_name = celeb_episode_detail["name"]
                    season_number = celeb_episode_detail["partOfSeason"]["seasonNumber"]
                    character = celeb_episode_detail["character"]["name"]
                    actor = celeb_episode_detail["actor"]["name"]
                    episode = celeb_episode_detail["episodeNumber"]
                    posted_by = other_desc["author"]["name"]
                    posted_on = other_desc["datePublished"]
                    tags = other_desc["keywords"]
                    description = other_desc["articleBody"].split("For shoppable links")[0]
                    img = other_desc["image"][0]["url"]

                    exact_similar = Selector(text=product_detail_req.text).xpath(
                        '//div[@class="products-wrap"]//span[@class="product-store"]//text()').extract()
                    exact_final_xpath = similar_final_xpath = None
                    exact_image = exact_store = exact_price = similar_image = similar_store = similar_price = ['']
                    for es in exact_similar:
                        exact_paths = '//div[@class="product-item  product-{}"]//img[@class="exact-match "]'.format(es)
                        similar_paths = '//div[@class="product-item  product-{}"]//img[@class="similar-match "]'.format(es)
                        tester1 = Selector(text=product_detail_req.text).xpath(exact_paths).extract()
                        if tester1:
                            exact_final_xpath = '//div[@class="product-item  product-{}"]'.format(es)
                        tester2 = Selector(text=product_detail_req.text).xpath(similar_paths).extract()
                        if tester2:
                            similar_final_xpath = '//div[@class="product-item  product-{}"]'.format(es)
                    if exact_final_xpath:
                        exact_image = Selector(text=product_detail_req.text).xpath(
                            exact_final_xpath+'//span[@class="product-item-image "]//img').xpath("@src").extract()
                        exact_store = Selector(text=product_detail_req.text).xpath(
                            exact_final_xpath+'//span[@class="product-store"]//text()').extract()
                        exact_price = Selector(text=product_detail_req.text).xpath(
                            exact_final_xpath+'//span[@class="product-price"]//text()').extract()
                    if similar_final_xpath:
                        similar_image = Selector(text=product_detail_req.text).xpath(
                            similar_final_xpath + '//span[@class="product-item-image "]//img').xpath("@src").extract()
                        similar_store = Selector(text=product_detail_req.text).xpath(
                            similar_final_xpath + '//span[@class="product-store"]//text()').extract()
                        similar_price = Selector(text=product_detail_req.text).xpath(
                            similar_final_xpath + '//span[@class="product-price"]//text()').extract()

                    print("title:",title,"\n","outfit_details:",outfit_details,"\n","series_name:",series_name,"\n"
                          ,"season_number:",season_number,"\n","character:",character,"\n","actor:",actor,"\n",
                          "episode:",episode,"\n","posted_by:",posted_by,"\n","posted_on:",posted_on,"\n",
                          "tags:",tags,"\n","description:",description,"\n","img:",img,"\n",
                          "exact_image:",base_url+exact_image[0],"\n","exact_store:",exact_store[0],"\n",
                          "exact_price:",exact_price[0],"\n","similar_image:",base_url+similar_image[0],"\n","similar_store:",similar_store[0],"\n",
                          "similar_price:",similar_price[0])

                    print("Completed link no. {} from total of {}".format(product_list.index(product_link) + 1,
                                                                          len(product_list)))
            print("Get all detail of show {}".format(show_name))

        else:
            print("Have some issues with the page.")
else:
    print("Have some issues with the site.")
