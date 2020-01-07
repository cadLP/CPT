# -*- coding: utf-8 -*-
import json
import re
import scrapy


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
                yield scrapy.Request(article_url, callback=self.parse_article)

        next_page = response.xpath('//li[has-class("a-pagination__item--next")]/a/@href').get()
        # print(next_page)
        next_page = response.urljoin(next_page)

        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_article(self, response):
        id = 0
        title = response.xpath('//meta[@name="title"]/@content').get()
        date_retrieved = ""
        date_published = response.xpath('//meta[@name="date"]/@content').get()
        date_edited = ""
        url = response.url
        content = response.xpath('//p/text()').getall()
        language = ""
        keywords = response.xpath('//meta[@name="keywords"]/@content').get()
        author = response.xpath('//meta[@name="author"]/@content').get()
        media = ""

        try:
            json_meta_obj = json.loads(response.xpath('//script[contains(@type, "ld+json")]/text()').get())
            date_edited = json_meta_obj["dateModified"]
        except:
            print(url + ": JSON object not found...")

        article_meta = {
            'id': id,
            'title': title,
            'date_retrieved': date_retrieved,
            'date_published': date_published,
            'date_edited': date_edited,
            'url': url,
            'content': content,
            'language': language,
            'keywords': keywords,
            'author': author,
            'media': media
        }

        yield article_meta
