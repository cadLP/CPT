# -*- coding: utf-8 -*-
import scrapy


class HeiseSpider(scrapy.Spider):
    name = 'heise'
    allowed_domains = ['heise.de']
    start_urls = ['https://www.heise.de/newsticker/it']

    def parse(self, response):
        url = response
