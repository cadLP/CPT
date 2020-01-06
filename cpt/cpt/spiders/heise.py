# -*- coding: utf-8 -*-
import re
import scrapy


class HeiseSpider(scrapy.Spider):
    name = 'heise'
    allowed_domains = ['www.heise.de']
    start_urls = ['https://www.heise.de/newsticker/it/']

    def parse(self, response):
        article_xpath = "//a[@class='a-article-teaser__link']/@href"
        article_url_regex = re.compile(r'/newsticker/meldung/.+?')

        for url in response.xpath(article_xpath).getall():
            if re.match(article_url_regex, url):
                # print(url)
                article_url = response.urljoin(url)
                yield scrapy.Request(article_url, callback=self.parse_article)

        next_page = response.xpath('//li[has-class("a-pagination__item--next")]/a/@href').get()
        # print(next_page)
        next_page = response.urljoin(next_page)

        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_article(self, response):
        print("Parsing...")
