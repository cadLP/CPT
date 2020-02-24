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

    def create_connection(self):
        """
        Creates a connection to the predefined database.
        """
        self.conn = psycopg2.connect(host="localhost", user="postgres", password="2522", dbname="NewspaperCrawler")
        self.conn.set_client_encoding('UTF8')
        self.cur = self.conn.cursor()

    def get_json(self, filename):
        """
        Getting all the scraped newspaper articles from the database.
        """



        SQL = """SELECT row_to_json(row)
                    FROM
                     (SELECT metadaten.*, text.article_text, raw_html.html, pos.pos_tags, method_pos.description as 
                     tagging_method_pos, ner.ner_tags, method_ner.description as tagging_method_pos
                    FROM metadaten
                    LEFT JOIN text ON text.metadaten_id=metadaten.id
                    LEFT JOIN raw_html ON metadaten.id=raw_html.metadaten_id
                    LEFT JOIN pos ON metadaten.id=pos.metadaten_id 
                    LEFT JOIN ner ON metadaten.id=ner.metadaten_id
                    LEFT JOIN method method_pos ON pos.method_id=method_pos.id
                    LEFT JOIN method method_ner ON ner.method_id=method_ner.id
                    ) row;"""

        known_spiders = ["sueddeutsche", "faz", "wiwo", "spiegel", "heise"]
        allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                         "Wissen", "Digital", "Karriere", "Reisen", "Technik"]

        self.cur.execute(SQL)
        result = self.cur.fetchall()

        with open(filename+".json", 'w', encoding='utf8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)

    def get_xml(self, filename):
        """
        Getting all the scraped newspaper articles from the database.
        """
        SQL = "SELECT database_to_xml(true, true, 'n');"

        self.cur.execute(SQL)
        for c in self.cur:
            with open(filename+".xml", 'w', encoding='utf8') as f:
                f.write(c[0])

    def get_sql_json(self, sql, filename):
        sql_row_json = """SELECT row_to_json(row) FROM ("""+sql+""") row;"""
        self.cur.execute(sql_row_json)

        result = self.cur.fetchall()

        with open(filename+".json", 'w', encoding='utf8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)


export = Export()
export.get_sql_json(sql="SELECT * FROM metadaten", filename="export")
