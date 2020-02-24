# -*- coding: utf-8 -*-
import scrapy
import json
from cpt.items import CptItem
from cpt import settings as cptssettings
import psycopg2


class FazSpider(scrapy.Spider):
    """
    This class is the Spider for the crawler of the FAZ
    """
    hostname = cptssettings.SERVER_ADRESS
    username = cptssettings.SERVER_USERNAME
    password = cptssettings.SERVER_USERPASSWORD
    database = cptssettings.SERVER_DATABASE

    categories = {
        "Politik": {"https://www.faz.net/aktuell/politik", "https://www.faz.net/aktuell/brexit/"},
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
        "Digital": {"https://www.faz.net/aktuell/technik-motor/digital/",
                    "https://www.faz.net/aktuell/wirtschaft/digitec/",
                    "https://www.faz.net/aktuell/finanzen/digital-bezahlen/"},
        "Wissen": {"https://www.faz.net/aktuell/wissen/"},
        "Regional": {"https://www.faz.net/aktuell/rhein-main/"},
        "Karriere": {"https://www.faz.net/aktuell/karriere-hochschule/"}
    }

    all_cat_list = ["Politik", "Wirtschaft", "Finanzen", "Sport", "Kultur", "Gesellschaft", "Reisen", "Digital", "Technik",
           "Meinung", "Wissen", "Regional", "Karriere"]

    selected_categories = []
    all_categories = []
    existing_urls = []

    def __init__(self, cat_list=[], *args, **kwargs):
        """
        All categories are stored in a dictionary. Here this dictionary will be converted into a list of all the
        relevant category URLs.
        A list of all existing URLs in the database will be created. This list will be compared to the parsed
        article urls.
        :param cat_list: A list of the categories that should be scraped.
        :type cat_list: list
        :param args:
        :param kwargs:
        """

        super(FazSpider, self).__init__(*args, **kwargs)
        for c in cat_list:
            for url in self.categories[c]:
                self.selected_categories.append(url)
        for c in self.all_cat_list:
            for url in self.categories[c]:
                self.all_categories.append(url)

        conn = psycopg2.connect(host="localhost", user="postgres", password="maybe", dbname="NewspaperCrawler")
        cur = conn.cursor()
        cur.execute("""SELECT url FROM metadaten;""")

        for a in cur:
            self.existing_urls.append(a[0])

    name = 'FAZSpider'
    start_urls = selected_categories

    def parse(self, response):
        """
        In this function we look for the links of the subcategories. Some of the predefined categories only
        consisted of subcategories, like "Meinung". So in this instance the links are being followed using the request method.
        For the other categories we loop through the results using a XPath Selector and follow these links.
        In both cases the the request uses the method parse_index as a callback.
        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader) and fed to the Spiders for processing
        :type response: dict
        """
        selector_subcategories = "//div[contains(@class, 'Articles')]//a[contains(@class, 'is-link') and starts-with(@href, '/aktuell')]/@href"

        if response.xpath(selector_subcategories).get():
            for faz_index in response.xpath(selector_subcategories).getall():
                if not any(faz_index in s for s in self.all_categories):
                    yield response.follow(faz_index, self.parse_index)
        else:
            request = scrapy.Request(response.url, callback=self.parse_index)
            yield request

    def parse_index(self, response):
        """
        This function will be called after the parse function. It loops through the results using a XPATH selector.
        The XPATH selects the links of the articles in the each subcategory. Most pages have the same setup, only the
        subcategory "Reise" has a different one. So there are two different XPATH selectors. Another restriction is,
        that links to blogs will not be selected.
        In addition the function looks for the link to the next page. This link yields a new request to the next page,
        registering itself as callback to handle the data extraction for the next page and to keep the crawling going
        through all the pages.
        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader)
        and fed to the Spiders for processing
        :type response: dict
        """

        selector_articles = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        selector_articles_reise = "//a[contains(@class, 'ContentLink') and contains(@href, '/reise/')]/@href"
        next_page_selector = '//li[contains(@class, "next-page")]/a/@href'


        if "reise" in response.url:
            for faz_article_r in response.xpath(selector_articles_reise).getall():
                if faz_article_r not in self.existing_urls:
                    yield response.follow(faz_article_r, self.parse_article)
        else:
            for faz_article in response.xpath(selector_articles).getall():
                if "blogs." not in faz_article:
                    if faz_article not in self.existing_urls:
                        yield response.follow(faz_article, self.parse_article)

                next_page = response.xpath(next_page_selector).get()
                self.logger.info('next_page %s', next_page)
                # if next_page is not None:
                #     yield response.follow(next_page, self.parse_index)

    def parse_article(self, response):
        """
        This function collects all the relevant data for the database from the articles. All relevant articles have
        an ld+json element in the source code. So this element will be used to collect most of the metadata.
        Another similar element (data-digital-data) lets us differentiate between payed and unpayed content.
        We will only scrape unpaid content. Keywords are not in the ld+json or the data-digital-data element,
        so it will be selected using XPATH. The metadata will be written into a scrapy item element.
        There are articles that are divided into multiple pages. To scrape these, the function looks for a link to the
        next page and yields a new request to it, registering parse_multiple_page_article as callback. In the new request
        the already scraped item will be handed over using the method meta.
        If there is only one page the item element will be the end result.
        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader)
        and fed to the Spiders for processing
        :type response: dict
        """

        metadata = json.loads(response.xpath('//div/@data-digital-data').get())

        try:
            metadata_ld = json.loads(
            response.xpath('//div[contains(@class, "Artikel")]//script[contains(@type, "ld+json")]/text()').get())
        except:
            metadata_ld = None
        keywords = response.xpath('//meta[contains(@name, "key")]/@content').get()
        next_page = response.xpath(
            "//li[contains(@class, 'next-page')]/a[contains(@class, 'Paginator_Link')]/@href").get()

        items = CptItem()

        if metadata_ld:
            if 'Bezahlartikel' not in metadata["article"]["type"]:
                try:
                    article_body = metadata_ld["articleBody"]
                except:
                    pass
                else:
                    title = metadata["page"]["title"]

                    try:
                        images = metadata_ld["image"]
                    except:
                        image_str = "no images"
                    else:
                        image_str = ""
                        if type(images) is list:
                            for img in images:
                                if not image_str:
                                    image_str += img["url"]
                                else:
                                    image_str = image_str + ", " + img["url"]
                        else:
                            image_str += images["url"]

                    try:
                        published = metadata_ld["datePublished"]
                    except:
                        published = "no date"

                    try:
                        modified = metadata_ld["dateModified"]
                    except:
                        modified = "no date"

                    try:
                        authors = metadata_ld["author"]
                    except:
                        author_str = "no author"
                    else:
                        author_str = ""
                        if type(authors) is list:
                            for author in authors:
                                if not author_str:
                                    author_str += author["name"]
                                else:
                                    author_str = author_str + ", " + author["name"]
                        else:
                            author_str += authors["name"]
                    category = "no category"
                    for key, values in self.categories.items():
                        for value in values:
                            if value in response.url:
                                category = key

                    items["title"] = title
                    items["author"] = author_str
                    items["date_published"] = published
                    items["date_edited"] = modified
                    items["url"] = response.url
                    items["language"] = "German"
                    items["keywords"] = keywords
                    items["media"] = image_str
                    items["article_text"] = article_body
                    items["category"] = category
                    items["raw_html"] = response.text
                    items["source"] = "faz.net"

                    if next_page:
                        yield response.follow(next_page, self.parse_multiple_page_article, meta={"item": items})
                    else:
                        yield items

    def parse_multiple_page_article(self, response):
        """
        This function will only be called if there are multiple pages to an article. Only the article text will need to
        be extended, so the rest of the metadata will be the same. If there are more than two pages the function looks
        for the link to the next page. This link yields a new request to the next page, registering itself as callback
        and handing over the current item.
        If there are no more next pages the item element will be the endresult.
        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader)
        and fed to the Spiders for processing
        :type response: dict
        """

        item = response.meta['item']
        metadata_ld = json.loads(
            response.xpath('//div[contains(@class, "Artikel")]//script[contains(@type, "ld+json")]/text()').get())
        next_page = response.xpath(
            "//li[contains(@class, 'next-page')]/a[contains(@class, 'Paginator_Link')]/@href").get()

        item["article_text"] = item["article_text"] + metadata_ld["articleBody"]
        item["raw_html"] = item["raw_html"] + response.text

        if next_page:
            yield response.follow(next_page, self.parse_multiple_page_article, meta={"item": response.meta['item']})
        else:
            yield item

