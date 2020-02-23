# -*- coding: utf-8 -*-
import json
import re
import scrapy
import psycopg2

from time import *
from ..items import CptItem


class HeiseSpider(scrapy.Spider):
    """ This class implements the spider for crawling the website heise.de"""
    categories = {
        "Politik": {'https://www.heise.de/newsticker/netzpolitik/'},
        "Wirtschaft": {'https://www.heise.de/newsticker/wirtschaft/'},
        "Finanzen": {},
        "Sport": {},
        "Kultur": {'https://www.heise.de/newsticker/entertainment/'},
        "Gesellschaft": {},
        "Reisen": {},
        "Technik": {'https://www.heise.de/newsticker/mobiles/'},
        "Meinung": {'https://www.heise.de/newsticker/journal/'},
        "Digital": {"https://www.heise.de/newsticker/it/"},
        "Wissen": {'https://www.heise.de/newsticker/wissen/'},
        "Regional": {},
        "Karriere": {}
    }

    all_cat_list = ["Politik", "Wirtschaft", "Finanzen", "Sport", "Kultur", "Gesellschaft", "Reisen", "Digital",
                    "Technik", "Meinung", "Wissen", "Regional", "Karriere"]

    selected_categories = []
    all_categories = []
    ducplicates_sql = """SELECT url FROM metadaten;"""

    categories = ["Digital"]

    def __init__(self, cat_list=[], *args, **kwargs):
        """
        All categories are stored in a dictionary. Here this dictionary will be converted into a list of all the relevant
        URLs.
        :param cat_list: A list of the categories that should be scraped.
        :type cat_list: list
        :param args:
        :param kwargs:
        """
        super(HeiseSpider, self).__init__(*args, **kwargs)
        for c in cat_list:
            for url in self.categories[c]:
                self.selected_categories.append(url)
        for c in self.all_cat_list:
            for url in self.categories[c]:
                self.all_categories.append(url)

        self.cur.execute(self.ducplicates_sql)
        for url in self.cur:
            self.known_urls.append(url[0])
        self.cur.close()

        def create_connection(self):
            """
            Creates a connection to the predefined database.
            """
            self.conn = psycopg2.connect(host=self.hostname, user=self.username, password=self.password,
                                         dbname=self.database)
            self.cur = self.conn.cursor()

    name = 'heise'
    allowed_domains = ['www.heise.de']
    start_urls = selected_categories

    def parse(self, response):
        """

        :param response:
        :return:
        """
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
        """

        :param response:
        :return:
        """
        items = CptItem()

        try:
            title = response.xpath('//meta[@name="title"]/@content').get()
        except:
            title = "no title"
        try:
            date_retrieved = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        except:
            date_retrieved = "no date"
        try:
            date_published = response.xpath('//meta[@name="date"]/@content').get()
        except:
            date_published = "no date"
        try:
            json_meta_obj = json.loads(response.xpath('//script[contains(@type, "ld+json")]/text()').get())
            date_edited = json_meta_obj[0]['dateModified']
        except:
            date_edited = "no date"
        # URL is instance variable of the response object
        url = response.url
        try:
            content = response.xpath('//article[@id="meldung"]/div/div/p/text()').getall()
        except:
            content = "no content"
        # Language is set to german by default
        language = "de"
        try:
            keywords = response.xpath('//meta[@name="keywords"]/@content').get()
        except:
            keywords = "no keywords"
        try:
            author = response.xpath('//meta[@name="author"]/@content').get()
        except:
            author = "no author"
        media = ""
        category = ""
        category_set = {'it', 'mobiles', 'entertainment', 'wissen',
                        'netzpolitik', 'wirtschaft', 'journal'}
        referrer_list = str(response.request.headers.get('Referer', None)).split("/")

        try:
            if referrer_list[-2] in category_set:
                category = referrer_list[-2]
            elif referrer_list[-3] in category_set:
                category = referrer_list[-3]
        except:
            category = "no category"

        items["title"] = title
        items["author"] = author
        # items["date_retrieved"] = date_retrieved
        items["date_published"] = date_published
        items["date_edited"] = date_edited
        items["url"] = url
        items["language"] = language
        items["keywords"] = keywords
        items["media"] = media
        items["article_text"] = content
        items["category"] = category
        # items["raw_html"] = str(response.headers) + response.text
        items["source"] = "Heise"

        yield items
