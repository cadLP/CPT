import scrapy
import logging


Politik = "https://www.faz.net/aktuell/politik"
Wirtschaft = "https://www.faz.net/aktuell/wirtschaft/"
Finanzen = "https://www.faz.net/aktuell/finanzen/"
Sport = "https://www.faz.net/aktuell/sport/"
Kultur = ["https://www.faz.net/aktuell/feuilleton/", "https://www.faz.net/aktuell/stil/"]
Gesellschaft = "https://www.faz.net/aktuell/gesellschaft/"
Reisen = "https://www.faz.net/aktuell/reise/"
Technik = "https://www.faz.net/aktuell/technik-motor/"
#Meinung
#IT/Digital
Wissen = "https://www.faz.net/aktuell/wissen/"
Regional = "https://www.faz.net/aktuell/rhein-main/"
Karriere = "https://www.faz.net/aktuell/karriere-hochschule/"


class FAZSpider(scrapy.Spider):
    name = 'faz_index'
    start_urls = [
        Technik
        #, Wirtschaft, Finanzen, Sport, Kultur, Kultur2, Gesellschaft, Reisen, Technik, Wissen, Regional, Karriere
    ]

    def parse(self, response):
        selector_subcategories = "//div[contains(@class, 'Articles')]//a[contains(@class, 'is-link') and starts-with(@href, '/aktuell')]/@href"

        for faz_index in response.xpath(selector_subcategories).getall():
            yield response.follow(faz_index, self.parse_index)

    def parse_index(self, response):

        selector_articles = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        #Fplus = "//span[contains(@class, 'Headline') and not(contains(@class, 'has-icon') or contains(@class, 'Text'))]"
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
        with open (filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)



#//div[contains(@class, 'Lead')]//a[contains(@class, 'is-link')]/@href
#//li[contains(@class, 'TopicsListItem')]/a[contains(@href, 'aktuell')]/@href
#link_selector = '//div[contains(@class, "Articles")]//a[contains(@class, "lbl-Base") and not(contains(@class, "lbl-Base-has-icon"))]/@href'
#scrapy runspider quotes_spider.py -o quotes.json