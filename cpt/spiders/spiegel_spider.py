# -*- coding: utf-8 -*-

import scrapy
import json
from cpt import settings as cptsettings
from ..items import CptItem
import psycopg2


class SpiegelSpider(scrapy.Spider):
    """
    This class defines the spider for crawling Spiegel.de together with selected urls, from which it should start
    crawling
    """
    hostname = cptsettings.SERVER_ADRESS
    username = cptsettings.SERVER_USERNAME
    password = cptsettings.SERVER_USERPASSWORD
    database = cptsettings.SERVER_DATABASE

    category = {"Politik": {"https://www.spiegel.de/politik/"},
                "Wirtschaft": {"https://www.spiegel.de/wirtschaft/"},
                "Sport": {"https://www.spiegel.de/sport/"},
                "Kultur": {"https://www.spiegel.de/kultur/"},
                "Gesellschaft": {"https://www.spiegel.de/deinspiegel/", "https://www.spiegel.de/reise/",
                                 "https://www.spiegel.de/stil/", "https://spiegel.de/thema/familie/"},
                "Technik": {"https://www.spiegel.de/wissenschaft/technik/", "https://www.spiegel.de/auto/"},
                "IT": {"https://www.spiegel.de/netzwelt/"},
                "Wissen": {"https://www.spiegel.de/gesundheit/", "https://www.spiegel.de/wissenschaft/"},
                "Karriere": {"https://www.spiegel.de/karriere/"}
                }

    selected_categories = []
    existing_urls = []

    def __init__(self, cat_list=[], *args, **kwargs):
        super(SpiegelSpider, self).__init__(*args, **kwargs)
        for c in cat_list:
            if c in self.category:
                for url in self.category[c]:
                    self.start_urls.append(url)

        self.conn = psycopg2.connect(host=self.hostname, user=self.username, password=self.password, dbname=self.database)
        self.cur = self.conn.cursor()
        self.cur.execute("""SELECT url FROM metadaten;""")

        for a in self.cur:
            self.existing_urls.append(a[0])

    name = "spiegel"
    start_urls = []

    def parse(self, response):
        """
        This function defines a next page selector with the help of an X-Path expression, as our spider crawls the selected
        start_urls. We also specify that every articles in start_urls containing a Title and Subtitle be crawled alongside.
        The variable "Test" containing a Boolean value limits the spider to crawling just the very first pages of the
        start_urls when set to True, but we get crawled data in till next pages, when set to False.

        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader)
        and fed to the Spiders for processing
        :return:
        """
        next_page = response.xpath(
            "//div[contains(@data-area,'pagination-bar')]//a[contains(@title,'Ältere')]/@href").get()
        urls = response.xpath("//h2[contains(@class,'w-')]/a/@href").getall()

        for url in urls:
            if url not in self.existing_urls:
                yield response.follow(url, self.parse_article)

        # if next_page is not None:
        #    yield response.follow(next_page, self.parse)

    def parse_article(self, response):

        """
        This function collects all the relevant data for the database from the articles. Metadata is collected
        using the ld+json element, which is add into the source code, thus enabling us easily differentiate between
        payed and unpayed content. We will only scrape unpaid content. Keywords are not in the ld+json element, so it
        will be selected using XPATH. The metadata will be written into a scrapy item element. The item element will be
        the end result.

        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader)
        and fed to the Spiders for processing
        :return:
        """

        metadata_selektor = json.loads(response.xpath('//head/script[@type="application/ld+json"]/text()').get())
        premium = response.xpath('//h2//span[contains(@data-contains-flags, "paid")]').get()
        body = response.xpath('//article//div[contains(@class, "RichText")]//p/text()').getall()

        if not premium:
            if metadata_selektor:
                self.logger.info("Scraping article: %s", response.url)
                meta = metadata_selektor[0]

                try:
                    title = meta["headline"]
                except:
                    title = "no_author"

                try:
                    date_published = meta["datePublished"]
                except:
                    date_published = "no date"

                try:
                    date_modified = meta["dateModified"]
                except:
                    date_modified = "no date"

                try:
                    authors = meta["author"]
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

                try:
                    images = meta["image"]
                except:
                    image_str = "no image"

                else:
                    image_str = ""
                    if type(images) is list:
                        for image in images:
                            if not image_str:
                                image_str += image
                            else:
                                image_str = image_str + ", " + image
                    else:
                        image_str += images

                try:
                    keywords = meta["keywords"]
                except:
                    keywords = "no keywords"

                body_str = ""
                for p in body:
                    if not body_str:
                        body_str += p
                    else:
                        body_str = body_str + " " + p
                article_category = "no category"
                for key, values in self.category.items():
                    for value in values:
                        if value in response.url:
                            article_category = key

                item = CptItem()
                item["title"] = title
                item["author"] = author_str
                item["date_published"] = date_published
                item["date_edited"] = date_modified
                item["url"] = response.url
                item["language"] = "German"
                item["keywords"] = keywords
                item["media"] = image_str
                item["article_text"] = body_str
                item["category"] = article_category
                item["raw_html"] = response.text
                item["source"] = "spiegel.de"

                yield item
