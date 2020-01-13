# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import CptItem

categories = {
    "Politik": {"https://www.faz.net/aktuell/politik", "https://www.faz.net/aktuell/brexit/"},
    "Wirtschaft": {"https://www.faz.net/aktuell/wirtschaft/"},
    "Finanzen": {"https://www.faz.net/aktuell/finanzen/"},
    "Sport": {"https://www.faz.net/aktuell/sport/"},
    "Kultur": {"https://www.faz.net/aktuell/feuilleton/", "https://www.faz.net/aktuell/stil/"},
    "Gesellschaft": {"https://www.faz.net/aktuell/gesellschaft/"},
    "Reisen": {"https://www.faz.net/aktuell/reise/"},
    "Technik": {"https://www.faz.net/aktuell/technik-motor/"},
    "Meinung": {"https://www.faz.net/aktuell/feuilleton/brief-aus-istanbul/",
                "https://www.faz.net/aktuell/rhein-main/buergergespraech/",
                "https://www.faz.net/aktuell/wirtschaft/hanks-welt/"},
    "Digital": {"https://www.faz.net/aktuell/technik-motor/digital/",
                "https://www.faz.net/aktuell/wirtschaft/digitec/",
                "https://www.faz.net/aktuell/finanzen/digital-bezahlen/"},
    "Wissen": {"https://www.faz.net/aktuell/wissen/"},
    "Regional": {"https://www.faz.net/aktuell/rhein-main/"},
    "Karriere": {"https://www.faz.net/aktuell/karriere-hochschule/"}
}

to_selected_cat = ["Wirtschaft"]
# "Digital", "Wirtschaft", "Finanzen", "Sport", "Kultur", "Gesellschaft", "Reisen", "Digital", "Technik", "Meinung", "Wissen", "Regional", "Karriere"
cat = ["Politik", "Wirtschaft", "Finanzen", "Sport", "Kultur", "Gesellschaft", "Reisen", "Digital", "Technik",
       "Meinung", "Wissen", "Regional", "Karriere"]

selected_categories = []
all_categories = []

for x, y in categories.items():
    for i in to_selected_cat:
        if i == x:
            for a in y:
                selected_categories.append(a)
    for i in cat:
        if i == x:
            for a in y:
                all_categories.append(a)

class FazSpider(scrapy.Spider):
    name = 'FAZSpider'
    start_urls = selected_categories

    def parse(self, response):
        selector_subcategories = "//div[contains(@class, 'Articles')]//a[contains(@class, 'is-link') and starts-with(@href, '/aktuell')]/@href"

        if response.xpath(selector_subcategories).get():
            for faz_index in response.xpath(selector_subcategories).getall():
                if not any(faz_index in s for s in all_categories):
                    # self.logger.info('Parse function calles on %s', response.url)
                    # self.logger.info('Parse %s', faz_index)
                    yield response.follow(faz_index, self.parse_index)
        else:
            # self.logger.info("Else: %s", response.url)
            request = scrapy.Request(response.url, callback=self.parse_index)
            yield request

    def parse_index(self, response):
        selector_articles = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        selector_articles_reise = "//a[contains(@class, 'ContentLink')]/@href"
        next_page_selector = '//li[contains(@class, "next-page")]/a/@href'

        if "reise" in response.url:
            for faz_article_r in response.xpath(selector_articles_reise).getall():
                # self.logger.info('Result Reise: %s', faz_article_r)
                yield response.follow(faz_article_r, self.parse_article)
        else:
            for faz_article in response.xpath(selector_articles).getall():
                if "blogs." not in faz_article:
                    # self.logger.info('Result: %s', faz_article)
                    # yield {"url": faz_article}
                    yield response.follow(faz_article, self.parse_article)

            next_page = response.xpath(next_page_selector).get()
            self.logger.info('next_page %s', next_page)
            # if next_page is not None:
            #    yield response.follow(next_page, self.parse_index)

    def parse_article(self, response):
        metadata = json.loads(response.xpath('//div/@data-digital-data').get())
        metadata_ld = json.loads(
            response.xpath('//div[contains(@class, "Artikel")]//script[contains(@type, "ld+json")]/text()').get())

        next_page = response.xpath(
            "//li[contains(@class, 'next-page')]/a[contains(@class, 'Paginator_Link')]/@href").get()
        payed_content = metadata["article"]["type"]

        items = CptItem()

        if 'Bezahlartikel' not in payed_content:
            try:
                article_body = metadata_ld["articleBody"]
            except:
                pass
            else:
                title = metadata["page"]["title"]

                try:
                    description = metadata_ld["description"]
                except:
                    description = "no description"

                try:
                    images = metadata_ld["image"]
                except:
                    image_str = "no images"
                else:
                    image_str = ""
                    if type(images) is list:
                        for img in images:
                            if not image_str:
                                image_str += img["url"]
                            else:
                                image_str = image_str + ", " + img["url"]
                    else:
                        image_str += images["url"]

                try:
                    pagination = metadata["article"]["pagination"]["maxPage"]
                except:
                    pagination = "1"

                try:
                    published = metadata_ld["datePublished"]
                except:
                    published = "no date"

                try:
                    modified = metadata_ld["dateModified"]
                except:
                    modified = "no date"

                try:
                    authors = metadata_ld["author"]
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

                for key, values in categories.items():
                    for value in values:
                        #self.logger.info("Value: %s", values)
                        #self.logger.info("Value: %s", value)
                        #self.logger.info("URL: %s", response.url)
                        if value in response.url:
                            category = key


                """article = {
                    'title': title,
                    'author': author_str,
                    'payed_content': payed_content,
                    'description': description,
                    'article_body': article_body,
                    'published': published,
                    'modified': modified,
                    'images': image_str,
                    'url': response.url,
                    'page_count': pagination
                }"""

                items["title"] = title
                items["author"] = author_str
                items["date_retrieved"] = "no date yet"
                items["date_published"] = published
                items["date_edited"] = modified
                items["url"] = response.url
                items["language"] = "German"
                items["keywords"] = "No Keywords"
                items["media"] = image_str
                items["article_text"] = article_body
                items["category"] = category

                if next_page:
                    yield response.follow(next_page, self.parse_multiple_page_article, meta={"item": items})
                else:
                    yield items

    def parse_multiple_page_article(self, response):
        item = response.meta['item']
        metadata_ld = json.loads(
            response.xpath('//div[contains(@class, "Artikel")]//script[contains(@type, "ld+json")]/text()').get())
        next_page = response.xpath(
            "//li[contains(@class, 'next-page')]/a[contains(@class, 'Paginator_Link')]/@href").get()

        item["article_text"] = item["article_text"] + metadata_ld["articleBody"]

        if next_page:
            yield response.follow(next_page, self.parse_multiple_page_article, meta={"item": response.meta['item']})
        else:
            yield item
