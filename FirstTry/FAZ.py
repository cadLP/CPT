import scrapy
import json


class FAZSpider(scrapy.Spider):
    name = 'faz_article'
    start_urls = [
        'https://www.faz.net/aktuell/wissen/medizin-ernaehrung/'
        #'https://www.faz.net/aktuell/wissen/weltraum/',
        #'https://www.faz.net/aktuell/wissen/leben-gene/', 'https://www.faz.net/aktuell/wissen/erde-klima/',
        #'https://www.faz.net/aktuell/wissen/physik-mehr/', 'https://www.faz.net/aktuell/wissen/archaeologie-altertum/',
        #'https://www.faz.net/aktuell/wissen/geist-soziales/', 'https://www.faz.net/aktuell/wissen/forschung-politik/'
    ]

    def parse(self, response):
        link_selector = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        next_page_selector = '//li[contains(@class, "next-page")]/a/@href'

        for faz_article in response.xpath(link_selector).getall():
            # self.logger.info('Parse function called on %s', response.url)
            yield response.follow(faz_article, self.parse_article)

        next_page = response.xpath(next_page_selector).get()
        self.logger.info('next_page %s', next_page)
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        metadata = json.loads(response.xpath('//div/@data-digital-data').get())
        metadata_ld = json.loads(
            response.xpath('//div[contains(@class, "Artikel")]//script[contains(@type, "ld+json")]/text()').get())

        next_page = response.xpath(
            "//li[contains(@class, 'next-page')]/a[contains(@class, 'Paginator_Link')]/@href").get()
        payed_content = metadata["article"]["type"]
        paragraph_1 = response.xpath("//[contains(@class , 'copy') and not (contains(@class , 'intro'))]/text()").getall()

        if 'Bezahlartikel' not in payed_content:
            title = metadata["page"]["title"]

            try:
                description = metadata_ld["description"]
            except:
                description = "no description"

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
                pagination = metadata["article"]["pagination"]["maxPage"]
            except:
                pagination = "1"

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

            try:
                article_body = metadata_ld["articleBody"]
            except:
                #article_body = "no article body"
                article_body = ""
                if paragraph_1:
                    for i in paragraph_1:
                        if not article_body:
                            article_body += i
                        else:
                            article_body = article_body + " " + i
                else:
                    article_body = "no article body"




            article = {
                'title': title,
                '#author': author_str,
                'payed_content': payed_content,
                'description': description,
                'article_body': article_body,
                'published': published,
                'modified': modified,
                'images': image_str,
                'url': response.url,
                'page_count': pagination
            }

            if next_page:
                yield response.follow(next_page, self.parse_multiple_page_article, meta={"item": article})
            else:
                yield article

    def parse_multiple_page_article(self, response):
        item = response.meta['item']
        metadata_ld = json.loads(
            response.xpath('//div[contains(@class, "Artikel")]//script[contains(@type, "ld+json")]/text()').get())
        next_page = response.xpath(
            "//li[contains(@class, 'next-page')]/a[contains(@class, 'Paginator_Link')]/@href").get()

        item["article_body"] = item["article_body"] + metadata_ld["articleBody"]

        if next_page:
            yield response.follow(next_page, self.parse_multiple_page_article, meta={"item": response.meta['item']})
        else:
            yield item

