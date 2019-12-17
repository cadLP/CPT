# -*- coding: utf-8 -*-
import scrapy


Politik = ["https://www.faz.net/aktuell/politik"]
Wirtschaft = ["https://www.faz.net/aktuell/wirtschaft/"]
Finanzen = ["https://www.faz.net/aktuell/finanzen/"]
Sport = ["https://www.faz.net/aktuell/sport/"]
Kultur = ["https://www.faz.net/aktuell/feuilleton/", "https://www.faz.net/aktuell/stil/"]
Gesellschaft = ["https://www.faz.net/aktuell/gesellschaft/"]
Reisen = ["https://www.faz.net/aktuell/reise/"]
Technik = ["https://www.faz.net/aktuell/technik-motor/"]
Meinung = ["https://www.faz.net/aktuell/feuilleton/brief-aus-istanbul/",
           "https://www.faz.net/aktuell/rhein-main/buergergespraech/",
           "https://www.faz.net/aktuell/wirtschaft/hanks-welt/"]
Digital = ["https://www.faz.net/aktuell/technik-motor/digital/", "https://www.faz.net/aktuell/wirtschaft/digitec/",
           "https://www.faz.net/aktuell/finanzen/digital-bezahlen/"]
Wissen = ["https://www.faz.net/aktuell/wissen/", "https://www.faz.net/aktuell/wirtschaft/schneller-schlau/"]
Regional = ["https://www.faz.net/aktuell/rhein-main/"]
Karriere = ["https://www.faz.net/aktuell/karriere-hochschule/"]

categories = Politik + Wirtschaft + Finanzen


class FazSpider(scrapy.Spider):
    name = 'FAZSpider'
    start_urls = categories

    def parse(self, response):
        selector_subcategories = "//div[contains(@class, 'Articles')]//a[contains(@class, 'is-link') and starts-with(@href, '/aktuell')]/@href"

        for faz_index in response.xpath(selector_subcategories).getall():
            yield response.follow(faz_index, self.parse_index)

    def parse_index(self, response):
        selector_articles = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        next_page_selector = '//li[contains(@class, "next-page")]/a/@href'

        for faz_article in response.xpath(selector_articles).getall():
            self.logger.info('Parse function called on %s', response.url)
            yield response.follow(faz_article, self.parse_article)

        next_page = response.xpath(next_page_selector).get()
        self.logger.info('next_page %s', next_page)
        if next_page is not None:
            yield response.follow(next_page, self.parse_index)

    def parse_article(self, response):
        article = response.url.split("/")[-1]
        filename = 'article-%s' % article
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
