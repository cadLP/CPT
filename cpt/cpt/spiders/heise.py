# -*- coding: utf-8 -*-
import scrapy


class HeiseSpider(scrapy.Spider):
    name = 'heise'
    allowed_domains = ['heise.de']
    start_urls = ['https://www.heise.de/newsticker/it/']

    def parse(self, response):
        article_xpath = "//article/a/@href"

        for url in response.xpath(article_xpath).getall():
            yield {
                scrapy.Request(url, callback=self.parse_article)
            }

        next_page = response.css('li.a-pagination__item').xpath('@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_article(self, response):
        pass