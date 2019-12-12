import scrapy


class FAZSpider(scrapy.Spider):
    name = 'faz_article'
    start_urls = [
        'https://www.faz.net/aktuell/politik/ausland/',
    ]

    def parse(self, response):
        link_selector = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        next_page_selector = '//li[contains(@class, "next-page")]/a/@href'

        for faz_article in response.xpath(link_selector).getall():
            yield {'url': faz_article}

        next_page = response.xpath(next_page_selector).get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

#scrapy runspider quotes_spider.py -o quotes.json
