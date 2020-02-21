# -*- coding: utf-8 -*-
import scrapy

class CptItem(scrapy.Item):
    """
    This class defines the fields for our items the Spiders store the data in.
    Field objects are used to specify metadata for each field.
    """
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
    html = scrapy.Field()
    source = scrapy.Field()
