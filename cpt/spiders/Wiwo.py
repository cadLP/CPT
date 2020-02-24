# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import CptItem
import re
import psycopg2
from cpt import settings as cptsettings

class WiwoSpider(scrapy.Spider):
    """
    This class creates the Spider for the crawler of the Wirtschaftswoche.
    """

    hostname = cptsettings.SERVER_ADRESS
    username = cptsettings.SERVER_USERNAME
    password = cptsettings.SERVER_USERPASSWORD
    database = cptsettings.SERVER_DATABASE
    categories = {
        "Politik": {"https://www.wiwo.de/politik/"},
        "Wirtschaft": {"https://www.wiwo.de/finanzen/", "https://www.wiwo.de/unternehmen/"},
        "Gesellschaft": {"https://www.wiwo.de/erfolg/trends/", "https://www.wiwo.de/technologie/green/"},
        "Technik": {"https://www.wiwo.de/technologie/"},
        "IT": {"https://www.wiwo.de/unternehmen/it/", "https://www.wiwo.de/technologie/digitale-welt/"},
        "Wissen": {"https://www.wiwo.de/unternehmen/energie/", "https://www.wiwo.de/technologie/umwelt/",
                   "https://www.wiwo.de/technologie/forschung/"},
        "Karriere": {"https://www.wiwo.de/erfolg/", "https://www.wiwo.de/erfolg/hochschule/"}
    }

    cat = ["Politik", "Wirtschaft", "Gesellschaft", "Technik", "IT", "Wissen", "Karriere"]
    #selected_cat = ["Wirtschaft"]

    selected_categories = []
    all_categories = []
    existing_urls = []

    def __init__(self, cat_list=[], *args, **kwargs):
        """
        All categories are stored in a dictionary. Here this dictionary will be converted into a list of all relevant
        URLs.
        :param cat_list: A list of the categories that should be scraped.
        :type cat_list: list
        :param args:
        :param kwargs:
        """
        super(WiwoSpider, self).__init__(*args, **kwargs)
        for c in cat_list:
            if c in self.categories:
                for url in self.categories[c]:
                    self.selected_categories.append(url)
        for c in self.cat:
            for url in self.categories[c]:
                self.all_categories.append(url)

        conn = psycopg2.connect(host=self.hostname, user=self.username, password=self.password, dbname=self.database)
        cur = conn.cursor()
        cur.execute("""SELECT url FROM metadaten;""")

        for a in cur:
            self.existing_urls.append(a[0])

    name = 'Wiwo'
    allowed_domains = ['www.wiwo.de']
    start_urls = selected_categories

    def parse(self, response):
        """
        In this function we extract the links to the subcategories based on the start url page and follow each link
        to the subcategories the x-path expression finds.
        """
        link_selector = "//h2[contains(@class,'ressort')]/a/@href"

        if response.xpath(link_selector).get():
            for wiwo_index in response.xpath(link_selector).getall():
                if not any(wiwo_index in s for s in self.all_categories):
                    yield response.follow(wiwo_index, self.parsecontent)
        else:
            request = scrapy.Request(response.url, callback=self.parsecontent)
            yield request

    def parsecontent(self, response):
        """
        This function is called after the parse function and we extract and follow the links of each article
        using an x-path expression which loops over the several subcategories. In case the subcategory has more
        than one page of articles, an x-path expression follows the link to the next page and extracts the
        articles from there.
        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader) and fed to the Spiders for processing
        :type response: dict
        """
        link_selector = response.xpath('//a[contains(@class, "teaser__image-wrapper")]/@href').getall()
        next_page = response.xpath('//a[contains(@rel,"next")]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parsecontent)
        for article in link_selector:
            if "https://www.wiwo.de"+article not in self.existing_urls:
                yield response.follow(article, self.parsearticle)

    def parsearticle(self, response):
        """
        This function collects all relevant article information to store in the database. All articles (except
        picture galleries, in which we are not interested) contains an ld+json object in their source code. This
        object contains the majority of data we are looking for (including date_published, date_modified, author,
        publisher, images and keywords). For the images we only store the corresponding link. If there are several
        authors, publishers, images or keywords we convert the given list into a string. The title is extracted directly
        from the source code. The article body is combined of the several paragraphs extracted by a x-path expression. To
        avoid losing information included in the text linked to another page we remove the HTML-tags and substitute them
        with "" using a regular expression. The category is chosen falling back on the dictionary 'categories' and
        for articles in subcategory not consistently following main category the longest link will be chosen.
        The metadata will be written into a scrapy item element.
        To reveal the payment status of the article we follow a x-path expression and scrape only the
        articles, which are freely accessible. Some articles are divided into more than one page. If this is tha case
        we follow the link to the button "Artikel auf einer Seite" and the whole content will be shown on one page,
        which we scrape like one-page articles and the item element will be the end result.
        :param response: A Response object represents an HTTP response, which is usually downloaded (by the Downloader)
        and fed to the Spiders for processing
        :type response: dict
        """

        items = CptItem()

        metadata_selektor = response.xpath('//script[contains(@type, "ld+json")]/text()').get()
        premium = response.xpath('//div[contains(@class, "c-metadata--premium")]').get()
        one_page = response.xpath('//a[contains(@data-command,"Paginierung-Artikel-auf-einer-Seite")]/@href').get()

        if one_page:
            if "https://www.wiwo.de"+one_page not in self.existing_urls:
                yield response.follow(one_page, self.parsearticle)
        else:
            if not premium:
                self.logger.info("Scraping article: %s", response.url)
                if metadata_selektor:
                    metadata = json.loads(metadata_selektor)

                    title = metadata["headline"]

                    try:
                        date_published = metadata["datePublished"]
                    except:
                        date_published = "no date"

                    try:
                        date_modified = metadata["dateModified"]
                    except:
                        date_modified = "no date"

                    try:
                        authors = metadata["author"]
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
                        publishers = metadata["publisher"]
                    except:
                        publisher_str = "no publisher"
                    else:
                        publisher_str = ""
                        if type(publishers) is list:
                            for publisher in publishers:
                                if not publisher_str:
                                    publisher_str += publisher["name"]
                                else:
                                    publisher_str = publisher_str + ", " + publisher["name"]
                        else:
                            publisher_str += publishers["name"]

                    try:
                        images = metadata["image"]
                    except:
                        image_str = "no image"
                    else:
                        image_str = ""
                        if type(images) is list:
                            for image in images:
                                if not image_str:
                                    image_str += image["url"]
                                else:
                                    image_str = image_str + ", " + image["url"]
                        else:
                            image_str += images["url"]

                    try:
                        keywords = metadata["keywords"]
                    except:
                        keywords_str = "no keywords"
                    else:
                        keywords_str = ""
                        if type(keywords) is list:
                            for keyword in keywords:
                                if not keywords_str:
                                    keywords_str += keyword
                                else:
                                    keywords_str = keywords_str + ", " + keyword

                    body = response.xpath('//div[contains(@class, "u-richtext")]/p').getall()
                    body_str = ""
                    for p in body:
                        if not body_str:
                            body_str += p
                        else:
                            body_str = body_str + " " + p
                    body_str = re.sub("<[^>]+?>", "", body_str)

                    category = "no category"
                    temp_max = 0
                    for key, values in self.categories.items():
                        for value in values:
                            if value in response.url and len(value)>temp_max:
                                temp_max = len(value)
                                category = key
                                category = str(category)

                    items['title'] = title
                    items['author'] = author_str
                    items['date_published'] = date_published
                    items['date_edited'] = date_modified
                    items['keywords'] = keywords_str
                    items['media'] = image_str
                    items['language'] = "german"
                    items['url'] = response.url
                    items['article_text'] = body_str
                    items['category'] = category
                    items['raw_html'] = response.text
                    items['source'] = "wiwo.de"

                    yield items
