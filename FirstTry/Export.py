import json
import psycopg2
from datetime import datetime
import pprint


#
# conn = psycopg2.connect('dbname=peterbecom')
# cur = conn.cursor()
# cur.execute()
# columns = ('id', 'oid', 'root', 'approved', 'name')
#
# results = []
# for row in cur.fetchall():
#     results.append(dict(zip(columns, row)))


class Export:

    def __init__(self):
        """
        The __init__ function will call all the other functions in the class. Depending on which tagging_method is
        added it will select the corresponding function.

        :param tagging_method: Selection which Tagging Method should be called.
        :type tagging_method: string
        """
        # super(Export, self).__init__(*args, **kwargs)
        self.create_connection()
        self.get_json()
        self.get_xml()

    def create_connection(self):
        """
        Creates a connection to the predefined database.
        """
        self.conn = psycopg2.connect(host="localhost", user="postgres", password="2522", dbname="NewspaperCrawler")
        self.conn.set_client_encoding('UTF8')
        self.cur = self.conn.cursor()

    def get_json(self):
        """
        Getting all the scraped newspaper articles from the database.

        """
        SQL = """SELECT row_to_json(row)
                    FROM
                     (SELECT metadaten.*, text.article_text, raw_html.html, pos.pos_tags, ner.ner_tags
                    FROM metadaten
                    FULL JOIN text ON text.metadaten_id=metadaten.id
                    FULL JOIN raw_html ON metadaten.id=raw_html.metadaten_id
                    FULL JOIN pos ON metadaten.id=pos.metadaten_id
                    FULL JOIN ner ON metadaten.id=ner.metadaten_id
                    ) row;"""

        self.cur.execute(SQL)
        result = self.cur.fetchall()

        with open('export.json', 'w', encoding='utf8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)

    def get_xml(self):
        """
        Getting all the scraped newspaper articles from the database.
        """
        SQL = "SELECT database_to_xml(true, true, 'n');"

        self.cur.execute(SQL)
        for c in self.cur:
            with open('export.xml', 'w', encoding='utf8') as f:
                f.write(c[0])


Export()
