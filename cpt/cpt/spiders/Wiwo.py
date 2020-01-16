# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import CptItem
import re

categories = {
    "Politik": {"https://www.wiwo.de/politik/"},
    "Wirtschaft": {"https://www.wiwo.de/finanzen/", "https://www.wiwo.de/unternehmen/"},
    "Gesellschaft": {"https://www.wiwo.de/erfolg/trends/", "https://www.wiwo.de/technologie/green/"},
    "Technik": {"https://www.wiwo.de/technologie/"},
    "IT": {"https://www.wiwo.de/unternehmen/it/", "https://www.wiwo.de/technologie/digitale-welt/"},
    "Wissen": {"https://www.wiwo.de/unternehmen/energie/", "https://www.wiwo.de/technologie/umwelt/",
               "https://www.wiwo.de/technologie/forschung/"},
    "Karriere": {"https://www.wiwo.de/erfolg/", "https://www.wiwo.de/erfolg/hochschule/"}
}

cat = ["Politik", "Wirtschaft", "Gesellschaft", "Technik", "IT", "Wissen", "Karriere"]
selected_cat = ["Politik"]

selected_categories = []
all_categories = []

for x, y in categories.items():
    for i in selected_cat:
        if i == x:
            for a in y:
                selected_categories.append(a)
    for i in cat:
        if i == x:
            for a in y:
                all_categories.append(a)


class WiwoSpider(scrapy.Spider):
    name = 'Wiwo'
    allowed_domains = ['www.wiwo.de']
    start_urls = selected_categories

    def parse(self, response):
        link_selector = "//h2[contains(@class,'ressort')]/a/@href"
        # for category in link_selector:
        #    self.logger.info("parse: %s",response.url)
        #    yield response.follow(category, self.parsecontent)


        if response.xpath(link_selector).get():
            for wiwo_index in response.xpath(link_selector).getall():
                if not any(wiwo_index in s for s in cat):
                    # self.logger.info('Parse function calles on %s', response.url)
                    # self.logger.info('Parse %s', faz_index)
                    yield response.follow(wiwo_index, self.parsecontent)
        else:
            # self.logger.info("Else: %s", response.url)
            request = scrapy.Request(response.url, callback=self.parsecontent)
            yield request

    def parsecontent(self, response):
        link_selector = response.xpath('//a[contains(@class, "teaser__image-wrapper")]/@href').getall()
        next_page = response.xpath('//a[contains(@rel,"next")]/@href').get()
        #if next_page:
        #   yield response.follow(next_page, self.parsecontent)
        for article in link_selector:
            yield response.follow(article, self.parsearticle)

    def parsearticle(self, response):
        self.logger.info("url: %s", response.url)

        items = CptItem()

        metadata_selektor = response.xpath('//script[contains(@type, "ld+json")]/text()').get()
        premium = response.xpath('//div[contains(@class, "c-metadata--premium")]').get()
        one_page = response.xpath('//a[contains(@data-command,"Paginierung-Artikel-auf-einer-Seite")]/@href').get()

        if one_page:
            self.logger.info("test: %s", one_page)
            yield response.follow(one_page, self.parsearticle)
        else:
            if not premium:
                if metadata_selektor:
                    metadata = json.loads(metadata_selektor)

                    title = metadata["headline"]

                    try:
                        date_published = metadata["datePublished"]
                    except:
                        date_published = "no date"

                    try:
                        date_modified = metadata["dateModified"]
                    except:
                        date_modified = "no date"

                    try:
                        description = metadata["description"]
                    except:
                        description = "no description"

                    try:
                        authors = metadata["author"]
                    except:
                        author_str = "no author"
                    else:
                        author_str = ""
                        if type(authors) is list:
                            for author in authors:
                                if not author_str:
                                    author_str += author["name"]
                                else:
                                    author_str = author_str + ", " + author["name"]
                        else:
                            author_str += authors["name"]

                    try:
                        publishers = metadata["publisher"]
                    except:
                        publisher_str = "no publisher"
                    else:
                        publisher_str = ""
                        if type(publishers) is list:
                            for publisher in publishers:
                                if not publisher_str:
                                    publisher_str += publisher["name"]
                                else:
                                    publisher_str = publisher_str + ", " + publisher["name"]
                        else:
                            publisher_str += publishers["name"]

                    try:
                        images = metadata["image"]
                    except:
                        image_str = "no image"
                    else:
                        image_str = ""
                        if type(images) is list:
                            for image in images:
                                if not image_str:
                                    image_str += image["url"]
                                else:
                                    image_str = image_str + ", " + image["url"]
                        else:
                            image_str += images["url"]

                    try:
                        keywords = metadata["keywords"]
                    except:
                        keywords = "no keywords"

                    body = response.xpath('//div[contains(@class, "u-richtext")]/p').getall() #/text()
                    body_str = ""
                    for p in body:
                        if not body_str:
                            body_str += p
                        else:
                            body_str = body_str + " " + p
                    body_str = re.sub("<[^>]+?>", "", body_str)

                    for key, values in categories.items():
                        for value in values:
                            if value in response.url:
                                category = key

                    items['title'] = title
                    items['author'] = author_str
                    items['date_retrieved'] = "no date"
                    items['date_published'] = date_published
                    items['date_edited'] = date_modified
                    items['keywords'] = keywords
                    items['media'] = image_str
                    items['language'] = "german"
                    items['url'] = response.url
                    items['article_text'] = body_str
                    items['category'] = category
                    #items['raw_html'] = str(response.headers) + response.text
                    items['source'] = "Wirtschaftswoche"

                    yield items


                    """article = {
                        'title': title,
                        'author': author_str,
                        'publisher': publisher_str,
                        'description': description,
                        'body': body_str,
                        'date_published': date_published,
                        'date_modified': date_modified,
                        'keywords': keywords,
                        'image': image_str,
                        'url': response.url,
                        'premium': premium
                        'language': language
                    }

                    yield article"""
