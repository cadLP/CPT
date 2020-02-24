# -*- coding: utf-8 -*-
"""
.. module:: spiegel_spider
    :synopsis: Spider for extracting data from spiegel.de

.. moduleauthor:: David  <s2dankon@uni-trier.de>
"""
import scrapy
import json
from ..items import CptItem


class SpiegelSpider(scrapy.Spider):
    """
    This class defines the spider for crawling Spiegel.de together with selected urls, from which it should start
    crawling
    """
    name = "spiegel"

    category = {"Politik": {"https://www.spiegel.de/politik/"}, "Wirtschaft": {"https://www.spiegel.de/wirtschaft/"},
                "Sport": {"https://www.spiegel.de/sport/"}, "Kultur": {"https://www.spiegel.de/kultur/"},
                "Gesellschaft": {"https://www.spiegel.de/deinspiegel/", "https://www.spiegel.de/reise/",
                                 "https://www.spiegel.de/stil/", "https://spiegel.de/thema/familie/"},
                "Technik": {"https://www.spiegel.de/wissenschaft/technik/", "https://www.spiegel.de/auto/"},
                "IT": {"https://www.spiegel.de/netzwelt/"}, "Wissen": {"https://www.spiegel.de/gesundheit/",
                                                                       "https://www.spiegel.de/wissenschaft/"},
                "Karriere": {"https://www.spiegel.de/karriere/"}
                }

    start_urls = []

    def __init__(self, cat_list=[], *args, **kwargs):
        super(SpiegelSpider, self).__init__(*args, **kwargs)
        for c in cat_list:
            for url in self.category[c]:
                self.start_urls.append(url)

    def parse(self, response):
        """
        This function defines a next page selector with the help of an X-Path expression, as our spider crawls the selected
        start_urls. We also specify that every articles in start_urls containing a Title and Subtitle be crawled alongside.
        The variable "Test" containing a Boolean value limits the spider to crawling just the very first pages of the
        start_urls when set to True, but we get crawled data in till next pages, when set to False.

        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader) and fed to the Spiders for processing
        :return:
        """
        next_page = response.xpath(
            "//div[contains(@data-area,'pagination-bar')]//a[contains(@title,'Ältere')]/@href").get()

        self.logger.info("URL beginn: %s", response.url)
        urls = response.xpath(
            "//h2[contains(@class,'w-')]/a/@href").getall()

        for url in urls:
            self.logger.info("URL: %s", response.url)
            yield response.follow(url, self.parse_article)

        test = True
        if not test:
            # if next_page is not None:
            self.logger.info("Page %s", next_page)
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):

        """
        This function collects all the relevant data for the database from the articles. Metadata is collected
        using the ld+json element, which is add into the source code, thus enabling us easily differentiate between
        payed and unpayed content. We will only scrape unpaid content. Keywords are not in the ld+json element, so it
        will be selected using XPATH. The metadata will be written into a scrapy item element. The item element will be
        the end result.

        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader) and fed to the Spiders for processing
        :return:
        """

        content = response.xpath("//p/text()").get()
        self.logger.info('content %s', content)
        self.logger.info('URL %s', response.url)

        metadata_selektor = json.loads(response.xpath('//head/script[@type="application/ld+json"]/text()').get())
        premium = response.xpath('//h2//span[contains(@data-contains-flags, "paid")]').get()

        if not premium:
            if metadata_selektor:
                meta = metadata_selektor[0]
                self.logger.info("JSON: %s", meta)
                self.logger.info("JSON: %s", metadata_selektor)
                self.logger.info("JSON: %s", type(metadata_selektor))

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

                body = response.xpath('//article//div[contains(@class, "RichText")]//p/text()').getall()

                body_str = ""
                for p in body:
                    if not body_str:
                        body_str += p
                    else:
                        body_str = body_str + " " + p

                item = CptItem()
                item["title"] = title
                item["author"] = author_str
                item["date_published"] = date_published
                item["date_edited"] = date_modified
                item["url"] = response.url
                item["language"] = "German"
                item["keywords"] = keywords
                item["media"] = image_str
                item["body"] = body_str
                # item["category"] = str(category)
                item["raw_html"] = response.text
                item["source"] = "spiegel.de"

                yield item
