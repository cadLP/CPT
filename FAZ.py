import scrapy
import json


class FAZSpider(scrapy.Spider):
    name = 'faz_article'
    start_urls = [
        'https://www.faz.net/aktuell/politik/ausland/',
    ]

    def parse(self, response):
        link_selector = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        #next_page_selector = '//li[contains(@class, "next-page")]/a/@href'

        for faz_article in response.xpath(link_selector).get():
            self.logger.info('Parse function called on %s', response.url)
            yield response.follow(faz_article, self.parse_article)

    def parse_article(self, response):
        title = response.xpath('//span[@class="atc-HeadlineEmphasisText"]/text()').get()
        subtitle = response.xpath('//span[@class="atc-HeadlineText"]/text()').get()
        author = response.xpath('//a[@class="atc-MetaAuthorLink"]/text()').get()
        article_source = response.xpath('//span[@class="atc-Footer_Quelle"]/text()').get()

        JSON = response.xpath('//script[contains(@type, "json")]').get()

        yield {
            #'title': title + ": " + subtitle,
            #'author': str(author) + "(" + str(article_source) + ")",
            'json': JSON
        }


        #article = response.url.split("/")[-1]
        #filename = 'article-%s' % article
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        #self.log('Saved file %s' % filename)

        #next_page = response.xpath(next_page_selector).get()
        #if next_page is not None:
        #    yield response.follow(next_page, self.parse)

#scrapy runspider quotes_spider.py -o quotes.json
