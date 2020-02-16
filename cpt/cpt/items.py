# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CptItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    date_retrieved = scrapy.Field()
    date_published = scrapy.Field()
    date_edited = scrapy.Field()
    url = scrapy.Field()
    language = scrapy.Field()
    keywords = scrapy.Field()
    media = scrapy.Field()
    article_text = scrapy.Field()
    category = scrapy.Field()
    raw_html = scrapy.Field()
    source = scrapy.Field()