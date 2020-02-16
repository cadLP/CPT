# -*- coding: utf-8 -*-
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from cpt.cpt.spiders import heise

# -*- coding: utf-8 -*-
import json
import re
import scrapy

from time import *

# from ..items import CptItem

categories = {}


class CptItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    date_retrieved = scrapy.Field()
    date_published = scrapy.Field()
    date_edited = scrapy.Field()
    url = scrapy.Field()
    language = scrapy.Field()
    keywords = scrapy.Field()
    media = scrapy.Field()
    article_text = scrapy.Field()
    category = scrapy.Field()
    source = scrapy.Field()


class HeiseSpider(scrapy.Spider):
    name = 'heise'
    allowed_domains = ['www.heise.de']
    start_urls = ['https://www.heise.de/newsticker/it/',
                  'https://www.heise.de/newsticker/mobiles/',
                  'https://www.heise.de/newsticker/entertainment/',
                  'https://www.heise.de/newsticker/wissen/',
                  'https://www.heise.de/newsticker/netzpolitik/',
                  'https://www.heise.de/newsticker/wirtschaft/',
                  'https://www.heise.de/newsticker/journal/']

    def parse(self, response):
        article_xpath = "//a[@class='a-article-teaser__link']/@href"
        article_url_regex = re.compile(r'/newsticker/meldung/.+?')

        for url in response.xpath(article_xpath).getall():
            if re.match(article_url_regex, url):
                # print(url)
                article_url = response.urljoin(url)
                yield scrapy.Request(article_url, callback=self.parse_article, meta={})

        next_page = response.xpath('//li[has-class("a-pagination__item--next")]/a/@href').get()
        next_page = response.urljoin(next_page)

        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_article(self, response):
        items = CptItem()

        id = 0
        title = response.xpath('//meta[@name="title"]/@content').get()
        date_retrieved = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        date_published = response.xpath('//meta[@name="date"]/@content').get()
        json_meta_obj = json.loads(response.xpath('//script[contains(@type, "ld+json")]/text()').get())
        date_edited = json_meta_obj[0]['dateModified']
        url = response.url
        content = response.xpath('//article[@id="meldung"]/div/div/p/text()').getall()
        language = "de"
        keywords = response.xpath('//meta[@name="keywords"]/@content').get()
        author = response.xpath('//meta[@name="author"]/@content').get()
        media = ""
        category = ""
        category_set = {'it', 'mobiles', 'entertainment', 'wissen',
                        'netzpolitik', 'wirtschaft', 'journal'}
        referrer_list = str(response.request.headers.get('Referer', None)).split("/")

        if referrer_list[-2] in category_set:
            category = referrer_list[-2]
        elif referrer_list[-3] in category_set:
            category = referrer_list[-3]

        items["title"] = title
        items["author"] = author
        items["date_retrieved"] = date_retrieved
        items["date_published"] = date_published
        items["date_edited"] = date_edited
        items["url"] = url
        items["language"] = language
        items["keywords"] = keywords
        items["media"] = media
        items["article_text"] = content
        items["category"] = category

        yield items


# Creates dictionary to store start url for each category
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

# Creates a list including every possible category
cat = ["Politik", "Wirtschaft", "Gesellschaft", "Technik", "IT", "Wissen", "Karriere"]
# Creates a list including the selected categories to crawl
selected_cat = ["Wirtschaft"]

# Creates two empty lists
selected_categories = []
all_categories = []

# Loop which ensures, that start urls for one category included in start urls from another category are left out during scraping
# Categories are appended to the empty lists above
for x, y in categories.items():
    for i in selected_cat:
        if i == x:
            for a in y:
                selected_categories.append(a)
    for i in cat:
        if i == x:
            for a in y:
                all_categories.append(a)


# Creates the spider
# Sets start_urls to the start urls defined in the dictionary 'categories'
class WiwoSpider(scrapy.Spider):
    name = 'Wiwo'
    allowed_domains = ['www.wiwo.de']
    start_urls = selected_categories

    # Creates x-path expression to the subcategories based on the start url page
    def parse(self, response):
        link_selector = "//h2[contains(@class,'ressort')]/a/@href"
        # for category in link_selector:
        #    self.logger.info("parse: %s",response.url)
        #    yield response.follow(category, self.parsecontent)

        # Follows each link to subcategories the x-path expression finds
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

    # Creates x-path expression to each article of a subcateory and follows it
    # Creates x-path expression to the next page of a subcategory and follows it
    def parsecontent(self, response):
        link_selector = response.xpath('//a[contains(@class, "teaser__image-wrapper")]/@href').getall()
        next_page = response.xpath('//a[contains(@rel,"next")]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parsecontent)
        for article in link_selector:
            yield response.follow(article, self.parsearticle)

    # Parses article information
    def parsearticle(self, response):
        self.logger.info("url: %s", response.url)

        # Connects Spider to Item Class
        items = CptItem()

        # Creates x-path expression to JSON-object including metadata of the article
        metadata_selektor = response.xpath('//script[contains(@type, "ld+json")]/text()').get()
        # Creates x-path expression to the information about the payment status of the article
        premium = response.xpath('//div[contains(@class, "c-metadata--premium")]').get()
        # Creates x-path expression to the button to show a several page article on one page
        one_page = response.xpath('//a[contains(@data-command,"Paginierung-Artikel-auf-einer-Seite")]/@href').get()

        # Follows x-path expression to show article on one page, if it is a multi-page article
        if one_page:
            self.logger.info("test: %s", one_page)
            yield response.follow(one_page, self.parsearticle)
        else:
            # Checks whether article is premium
            if not premium:
                # Loads JSON-object and extracts metadata
                # (title, date_published, date_modified, authors, media, article text, keywords, category)
                # If there is no entry sets variable to string e.g. "no date"
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
                    # If authors field is a list converts it to string while adressing attribute 'name'
                    # Creates empty string 'author_str' and iterates over list of authors
                    # Adds each author to 'author_str'
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
                        keywords_str = "no keywords"
                    else:
                        keywords_str = ""
                        if type(keywords) is list:
                            for keyword in keywords:
                                if not keywords_str:
                                    keywords_str += keyword
                                else:
                                    keywords_str = keywords_str + ", " + keyword

                    # Extracts body text of article through following x-path expression
                    body = response.xpath('//div[contains(@class, "u-richtext")]/p').getall()  # /text()
                    body_str = ""
                    # Combines several paragraphs 'p' to one article body 'body_str'
                    for p in body:
                        if not body_str:
                            body_str += p
                        else:
                            body_str = body_str + " " + p
                    # Removes HTML-tags substituting the tags with "" using a regular expression
                    # Avoids losing information included in text linked to another page
                    body_str = re.sub("<[^>]+?>", "", body_str)

                    # Returns category of article falling back on dictionary 'categories'
                    # Ensures category for articles in subcategory not consitently following main category is specified correctly
                    # choosing longest link
                    temp_max = 0
                    for key, values in categories.items():
                        for value in values:
                            if value in response.url and len(value) > temp_max:
                                temp_max = len(value)
                                category = key
                                category = str(category)

                    # Creates items using extracted metadata
                    items['title'] = title
                    items['author'] = author_str
                    # Value is defined in pipeline
                    items['date_retrieved'] = "no date"
                    items['date_published'] = date_published
                    items['date_edited'] = date_modified
                    items['keywords'] = keywords_str
                    items['media'] = image_str
                    # Value is set
                    items['language'] = "german"
                    items['url'] = response.url
                    items['article_text'] = body_str
                    items['category'] = category
                    # Raw HTML is combined of HTMl-header and HTML-text
                    items['html'] = str(response.headers) + response.text
                    # Value is set
                    items['source'] = "Wirtschaftswoche"

                    # Yields all items defined in 'items.py'
                    yield items


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(heise)
    yield runner.crawl(WiwoSpider)
    reactor.stop()


crawl()
reactor.run()
