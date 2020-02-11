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
        self.store_db_metadata(item)
        self.store_db_text(item)
        #self.store_db_html(item)
        return item

    def store_db_metadata(self, item):
        SQL = """INSERT INTO metadaten (title, date_retrieved, date_published, date_edited, url,
                language, keywords, media, id, authors, category, source)
                VALUES (%s, current_date, %s, %s, %s, %s, %s, %s, default, %s, %s, %s)
                ON CONFLICT (url)
                DO NOTHING;"""
        data = (item["title"],
                item["date_published"],
                item["date_edited"],
                item["url"],
                item["language"],
                item["keywords"],
                item["media"],
                item["author"],
                item["category"],
                item["source"])

        self.cur.execute(SQL, data)
        self.conn.commit()

    def store_db_text(self, item):
        SQL = """INSERT INTO text (article_text, metadaten_id)
             VALUES (%s, (SELECT id FROM metadaten WHERE url=%s));"""
        data = (item["article_text"], item["url"])

        self.cur.execute(SQL, data)
        self.conn.commit()

    def store_db_html(self, item):
        SQL = """INSERT INTO raw_html (html, metadaten_id)
             VALUES (%s, (SELECT id FROM metadaten WHERE url=%s));"""
        data = (item["html"], item["url"])

        self.cur.execute(SQL, data)
        self.conn.commit()
