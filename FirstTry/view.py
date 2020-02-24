import psycopg2


class View:

    def __init__(self, sql):
        """
        The __init__ function will call all the other functions in the class. Depending on which tagging_method is
        added it will select the corresponding function.
        """
        self.sql = sql
        self.create_connection()
        self.view_data()

    def create_connection(self):
        """
        Creates a connection to the predefined database.
        """
        self.conn = psycopg2.connect(host="localhost", user="postgres", password="2522", dbname="NewspaperCrawler")
        self.cur = self.conn.cursor()

    def view_data(self):
        """
        Getting all the scraped newspaper articles from the database.

        """
        self.cur.execute(self.sql)
        result = self.cur.fetchall()

        for r in result:
            print(r)


View("""SELECT * FROM metadaten""")
