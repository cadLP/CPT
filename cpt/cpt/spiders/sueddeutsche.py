# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import CptItem
import psycopg2


class SueddeutscheSpider(scrapy.Spider):
    hostname = "localhost"
    username = "postgres"
    password = "maybe"
    database = "NewspaperCrawler"
    known_urls = []

    category_urls = {
        "Politik": {"https://www.sueddeutsche.de/politik"},
        "Wirtschaft": {"https://www.sueddeutsche.de/wirtschaft"},
        "Meinung": {"https://www.sueddeutsche.de/meinung"},
        "Sport": {"https://www.sueddeutsche.de/sport"},
        "Regional": {"https://www.sueddeutsche.de/muenchen", "https://www.sueddeutsche.de/bayern"},
        "Kultur": {"https://www.sueddeutsche.de/kultur"},
        "Gesellschaft": {"https://www.sueddeutsche.de/leben", "https://www.sueddeutsche.de/panorama"},
        "Wissen": {"https://www.sueddeutsche.de/wissen"},
        "Digital": {"https://www.sueddeutsche.de/digital"},
        "Karriere": {"https://www.sueddeutsche.de/karriere"},
        "Reisen": {"https://www.sueddeutsche.de/reise"},
        "Technik": {"https://www.sueddeutsche.de/auto"},
    }
    start_urls = []
    allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                     "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
    ducplicates_sql = """SELECT url FROM metadaten;"""

    categories = ["Kultur"]
   # for c in categories:
   #     for url in category_urls[c]:
   #         start_urls.append(url)

    def __init__(self, cat_list=[], *args, **kwargs):
        super(SueddeutscheSpider, self).__init__(*args, **kwargs)
        for c in cat_list:
            for url in self.category_urls[c]:
                self.start_urls.append(url)
        self.create_connection()

        self.cur.execute(self.ducplicates_sql)
        for url in self.cur:
            self.known_urls.append(url[0])
        self.cur.close()

    def create_connection(self):
        """
        Creates a connection to the predefined database.
        """
        self.conn = psycopg2.connect(host=self.hostname, user=self.username, password=self.password, dbname=self.database)
        self.cur = self.conn.cursor()


    def start_requests(self):
        """
        Adds Urls already in the database to exclusion list.
        """
        # self.create_connection()
        # self.cur.execute(self.ducplicates_sql)
        # for url in self.cur:
        #     self.known_urls.append(url[0])
        # self.cur.close()

        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    name = 'sueddeutsche'
    allowed_domains = ['sueddeutsche.de']

    def parse(self, response):

        button_id = response.xpath("//body/@data-page-id").get()
        button_url = "https://www.sueddeutsche.de/overviewpage/additionalDepartmentTeasers?departmentId="+button_id+"&offset=0&size=25"

        yield scrapy.Request(button_url, self.parselist, meta={"button": button_id, "counter": 0})

        """urls = response.css('a.sz-button--small').xpath('@href').getall()
        for url in urls:
            yield scrapy.Request(url, callback=self.parsethema)"""

    def parselist(self, response):
        button_id = response.meta["button"]
        counter = response.meta["counter"]
        if response.xpath('//body[@class="szde-errorpage"]').get() is not None:
            return
        counter += 1
        offset = str(counter*25)
        next_url = "https://www.sueddeutsche.de/overviewpage/additionalDepartmentTeasers?departmentId="+button_id+"&offset="+offset+"&size=25"
        urls = response.css('div.sz-teaserlist-element--separator-line').xpath('a/@href').getall()
        for url in urls:
            if url not in self.known_urls:
                yield scrapy.Request(url, self.parsearticle)

        yield scrapy.Request(next_url, callback=self.parselist, meta={"button": button_id, "counter": counter})

    """def parsethema(self, response):
        urls = response.css('div.sz-teaserlist-element').xpath('a/@href').getall()
        nextpage = response.css('.pagination__page--next').xpath('@href').get()
        for url in urls:
            yield scrapy.Request(url, self.parsearticle)
        if nextpage:
            yield scrapy.Request(nextpage, callback=self.parsethema)"""

    def parsearticle(self, response):
        # abgabe 25.02 + prüfung
        # Todo check for article schon in db, logging, fehler?, erfolgreich? was?
        # prüfung: 20 min vortrag, am besten live presentation
        data = json.loads(response.xpath("//head/script[@type='application/ld+json']/text()").get())
        paiddata = response.xpath("//head/script[@type='text/javascript']/text()").get()[13:-1]
        try:
            paid = json.loads(paiddata)["pcat"]
        except:
            paid = "paid"
        if paid == "paid":
            return

        text_path = "//body/div[@id='sueddeutsche']/div/main/div/article/div[3]"
        texts = response.xpath(text_path+"/p/text() | "+text_path+"/p/a/text() | "+text_path+"/h4/text() | "+text_path+"/h3/text()").getall()

        text = ""
        intro_path = "//body/div[@id='sueddeutsche']/div/main/div/article/div[2]"
        intros = response.xpath(intro_path+"/p/text() | "+intro_path+"/div/ul/li/text() | "+intro_path+"/div/ul/li/a/text()").getall()
        first = True
        for intro in intros:
            if not first:
                text += (" "+intro)
            else:
                text += intro
                first = False

        for text_part in texts:
            if text_part[-1] not in "\".?!":
                text_part += "."
            if not first:
                text += (" "+text_part)
            else:
                text += text_part
                first = False

        category = ""
        url = response.url
        cat_url_parts = url.split("/")
        cat_url = "https://"+cat_url_parts[2]+"/"+cat_url_parts[3]
        for key, value in self.category_urls.items():
            if cat_url in value:
                category = key

        try:
            title = data["headline"]
        except:
            title = "no_title"
        try:
            published = data["datePublished"][0:10]
        except:
            published = "no_date"
        try:
            modified = data["dateModified"][0:10]
        except:
            modified = "no_date"
        try:
            image_url = data["image"]["url"]
        except:
            image_url = "no_url"
        try:
            keywords = data["keywords"]
        except:
            keywords = "no_keywords"
        try:
            authors = data["author"]
        except:
            authors = "no_authors"

        authornames = ""
        if not authors == "no_authors":
            for author in authors:
                authorname = author["name"]
                authornames += authorname
        if authornames == "":
            authornames = "no_authors"

        item = CptItem()
        item["title"] = title
        item["author"] = authornames
        item["date_published"] = published
        item["date_edited"] = modified
        item["url"] = response.url
        item["language"] = "German"
        item["keywords"] = keywords
        item["media"] = image_url
        item["article_text"] = text
        item["category"] = str(category)
        item["raw_html"] = response.text
        item["source"] = "Sueddeutsche.de"

        yield item
        #yield {url: self.known_urls}