# -*- coding: utf-8 -*-
import scrapy


class SueddeutscheSpider(scrapy.Spider):
    name = 'sueddeutsche'
    allowed_domains = ['sueddeutsche.de']
    start_urls = ['http://sueddeutsche.de/kultur']

    def parse(self, response):
        urls = response.css('a.sz-button--small').xpath('@href').getall()
        for url in urls:
            yield scrapy.Request(url, callback=self.parsethema)

    def parsethema(self, response):
        urls = response.css('div.sz-teaserlist-element--separator-line').xpath('a/@href').getall()
        nextpage = response.css('.pagination__page--next').xpath('@href').get()
        for url in urls:
            yield {"url": url}, scrapy.Request(url, self.parsearticle)
        if nextpage:
            yield scrapy.Request(nextpage, callback=self.parsethema)

    def parsearticle(self, response):
        pass
