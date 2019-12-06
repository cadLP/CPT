import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class FAZIndexSpider(CrawlSpider):
    name = 'faz_index'
    allowed_domains = ['faz.net']
    start_urls = [
        'https://www.faz.net/aktuell/',
    ]

    rules = (
        Rule(LinkExtractor(allow=('/aktuell/.*'))),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = scrapy.Item()
        item['author'] = response.xpath('//div[contains(@class, "atc-Meta")]//span[@class="atc-MetaAuthor"]/text()').getall()
        item['text'] = response.xpath('//div[contains(@class, "Text")]//p[contains(@class, "TextParagraph")]/text()').getall()
        return item



#link_selector = '//div[contains(@class, "Articles")]//a[contains(@class, "lbl-Base") and not(contains(@class, "lbl-Base-has-icon"))]/@href'
#scrapy runspider quotes_spider.py -o quotes.json