import scrapy
import json
import ast


class FAZSpider(scrapy.Spider):
    name = 'faz_article'
    start_urls = [
        'https://www.faz.net/aktuell/politik/ausland/',
    ]

    def parse(self, response):
        link_selector = '//div[contains(@class, "ctn-List")]//a[contains(@class, "ContentLink")]/@href'
        #next_page_selector = '//li[contains(@class, "next-page")]/a/@href'

        for faz_article in response.xpath(link_selector).getall():
            #self.logger.info('Parse function called on %s', response.url)
            yield response.follow(faz_article, self.parse_article)

    def parse_article(self, response):
        metadata = response.xpath('//div/@data-digital-data').get()
        metadata_2 = response.xpath('//div[contains(@class, "Artikel")]//script[contains(@type, "ld+json")]/text()').get()

        metadata_json = json.loads(metadata)

        metadata_2_json = json.loads(metadata_2)


        title = metadata_json["page"]["title"]
        author = metadata_json["article"]["author"]
        payed_content = metadata_json["article"]["type"]

        description = metadata_2_json["description"]
        article_body = metadata_2_json["articleBody"]
        published = metadata_2_json["datePublished"]
        modified = metadata_2_json["dateModified"]
        author = metadata_2_json["author"]["name"]

        images = []
        for img in metadata_2_json["image"]:
            images.append(img["url"])

        if 'Bezahlartikel' not in payed_content:
            yield {
                'title': title,
                'author': author,
                'payed_content': payed_content,
                'description': description,
                'article_body': article_body,
                'published': published,
                'modified': modified,
                'images': images,
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
