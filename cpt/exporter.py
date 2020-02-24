import json
import psycopg2
from cpt import settings as cptsettings
import pprint


class Export:
    """
    This class is used to export the database entries o files in different ways.
    """
    hostname = cptsettings.SERVER_ADRESS
    username = cptsettings.SERVER_USERNAME
    password = cptsettings.SERVER_USERPASSWORD
    database = cptsettings.SERVER_DATABASE

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
        self.conn = psycopg2.connect(host=self.hostname, user=self.username, password=self.password, dbname=self.database)
        self.conn.set_client_encoding('UTF8')
        self.cur = self.conn.cursor()

    def get_json(self, filename, source=[], categories=[]):
        """
        This methods exports all database entries depending on selected sources and categories
        to a filename.json.
        :param filename:
        :param source:
        :param categories:
        :return:
        """

        select_spiders_sql = ""
        for i in source:
            if i == "faz":
                select_spiders_sql += "SOURCE='" + i + ".net' OR "
            else:
                select_spiders_sql += "SOURCE='" + i + ".de' OR "

        select_cat_sql = ""
        for i in categories:
            select_cat_sql += "CATEGORY='" + i + "' OR "

        selected_sql = "WHERE (" + select_spiders_sql[:-4] + ") AND (" + select_cat_sql[:-4] + ")"

        SQL = """SELECT row_to_json(row)
                    FROM
                     (SELECT metadaten.*, text.article_text, pos.pos_tags, method_pos.description as 
                     tagging_method_pos, ner.ner_tags, method_ner.description as tagging_method_pos
                    FROM metadaten
                    LEFT JOIN text ON text.metadaten_id=metadaten.id
                    LEFT JOIN raw_html ON metadaten.id=raw_html.metadaten_id
                    LEFT JOIN pos ON metadaten.id=pos.metadaten_id 
                    LEFT JOIN ner ON metadaten.id=ner.metadaten_id
                    LEFT JOIN method method_pos ON pos.method_id=method_pos.id
                    LEFT JOIN method method_ner ON ner.method_id=method_ner.id """ + selected_sql + """) row;"""

        self.cur.execute(SQL)
        result = self.cur.fetchall()
        print("got result")
        with open(filename+".json", 'w', encoding='utf8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)

    def get_xml(self, filename):
        """
        This method exports the entire database to a filename.xml.
        :param filename:
        :return:
        """
        SQL = "SELECT database_to_xml(true, true, 'n');"

        self.cur.execute(SQL)
        for c in self.cur:
            with open(filename+".xml", 'w', encoding='utf8') as f:
                f.write(c[0])

    def get_sql_json(self, sql, filename):
        """
        This method exports the result of a sql query to a filename.json.
        :param sql:
        :param filename:
        :return:
        """

        sql_row_json = """SELECT row_to_json(row) FROM ("""+sql+""") row;"""
        self.cur.execute(sql_row_json)

        result = self.cur.fetchall()

        with open(filename+".json", 'w', encoding='utf8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)
