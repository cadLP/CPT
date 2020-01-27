# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2

hostname = "localhost"
username = "postgres"
password = "2522"
database = "NewspaperCrawler"

class FazPipeline(object):

    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        self.cur.execute(
            """Insert into metadaten (title, date_retrieved, date_published, date_edited, url, language, keywords, media, id, authors, category, source)
            values (%s, current_date, %s, %s, %s, %s, %s, %s, default, %s, %s, 'FAZ')""", (
                item['title'],
                item["date_published"],
                item["date_edited"],
                item["url"],
                item["language"],
                item["keywords"],
                item["media"],
                item["author"],
                item["category"]
            ))
        self.conn.commit()
