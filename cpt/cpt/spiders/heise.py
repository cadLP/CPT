# -*- coding: utf-8 -*-
import json
import re
import scrapy

from time import *
from ..items import CptItem

categories = {}


class HeiseSpider(scrapy.Spider):
    """ This class implements the spider for crawling the website heise.de"""
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
        items["raw_html"] = str(response.headers) + response.text
        items["source"] = "Heise"

        yield items
