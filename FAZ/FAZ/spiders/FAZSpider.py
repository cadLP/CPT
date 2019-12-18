# -*- coding: utf-8 -*-
import scrapy

categories = {
    "Politik": {"https://www.faz.net/aktuell/politik"},
    "Wirtschaft": {"https://www.faz.net/aktuell/wirtschaft/"},
    "Finanzen": {"https://www.faz.net/aktuell/finanzen/"},
    "Sport": {"https://www.faz.net/aktuell/sport/"},
    "Kultur": {"https://www.faz.net/aktuell/feuilleton/", "https://www.faz.net/aktuell/stil/"},
    "Gesellschaft": {"https://www.faz.net/aktuell/gesellschaft/"},
    "Reisen": {"https://www.faz.net/aktuell/reise/"},
    "Technik": {"https://www.faz.net/aktuell/technik-motor/"},
    "Meinung": {"https://www.faz.net/aktuell/feuilleton/brief-aus-istanbul/",
                "https://www.faz.net/aktuell/rhein-main/buergergespraech/",
                "https://www.faz.net/aktuell/wirtschaft/hanks-welt/"},
    "Digital": {"https://www.faz.net/aktuell/technik-motor/digital/", "https://www.faz.net/aktuell/wirtschaft/digitec/",
                "https://www.faz.net/aktuell/finanzen/digital-bezahlen/"},
    "Wissen": {"https://www.faz.net/aktuell/wissen/", "https://www.faz.net/aktuell/wirtschaft/schneller-schlau/"},
    "Regional": {"https://www.faz.net/aktuell/rhein-main/"},
    "Karriere": {"https://www.faz.net/aktuell/karriere-hochschule/"}
}

to_selected_cat = ["Reisen", "Digital"]

selected_categories = []

for x,y in categories.items():
    for i in to_selected_cat:
        if i == x:
            for a in y:
                selected_categories.append(a)

class FazSpider(scrapy.Spider):
    name = 'FAZSpider'
    start_urls = selected_categories

    def parse(self, response):
        selector_subcategories = "//div[contains(@class, 'Articles')]//a[contains(@class, 'is-link') and starts-with(@href, '/aktuell')]/@href"

        if response.xpath(selector_subcategories).get():
            for faz_index in response.xpath(selector_subcategories).getall():
                if not any(faz_index in s for s in categories):
                    #self.logger.info('Parse function calles on %s', response.url)
                    #self.logger.info('Parse %s', faz_index)
                    yield response.follow(faz_index, self.parse_index)
        else:
            #self.logger.info("Else: %s", response.url)
            request = scrapy.Request(response.url, callback=self.parse_index)
            yield request

    def parse_index(self, response):
        selector_articles = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        selector_articles_reise = "//a[contains(@class, 'ContentLink')]/@href"
        next_page_selector = '//li[contains(@class, "next-page")]/a/@href'

        if "reise" in response.url:
            for faz_article_r in response.xpath(selector_articles_reise).getall():
                #self.logger.info('Result Reise: %s', faz_article_r)
                yield response.follow(faz_article_r, self.parse_article)
        else:
            for faz_article in response.xpath(selector_articles).getall():
                if "blogs." not in faz_article:
                    #self.logger.info('Result: %s', faz_article)
                    #yield {"url": faz_article}
                    yield response.follow(faz_article, self.parse_article)

            """next_page = response.xpath(next_page_selector).get()
            self.logger.info('next_page %s', next_page)
            if next_page is not None:
                yield response.follow(next_page, self.parse_index)"""

    def parse_article(self, response):
        """article = response.url.split("/")[-1]
        filename = 'article-%s' % article
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)"""
        self.logger.info("URL: %s", response.url)

# //div[contains(@class, 'Lead')]//a[contains(@class, 'is-link')]/@href
# //li[contains(@class, 'TopicsListItem')]/a[contains(@href, 'aktuell')]/@href
# link_selector = '//div[contains(@class, "Articles")]//a[contains(@class, "lbl-Base") and not(contains(@class, "lbl-Base-has-icon"))]/@href'
# scrapy runspider quotes_spider.py -o quotes.json
