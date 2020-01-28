# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2


class CptPipeline(object):

    def open_spider(self, spider):
        hostname = 'localhost'
        username = 'crawler'
        password = ''
        database = 'crawler'
        self.conneciton = psycopg2.connect(host=hostname, user=username,
                                           password=password, database=database)
        self.cur = self.conneciton.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.conneciton.close()

    def process_item(self, item, spider):
        return item
