import psycopg2
from cpt import settings as cptsettings


class Viewer:
    """
    This class is used to get viewable results of an sql query from the database.
    """
    hostname = cptsettings.SERVER_ADRESS
    username = cptsettings.SERVER_USERNAME
    password = cptsettings.SERVER_USERPASSWORD
    database = cptsettings.SERVER_DATABASE

    def __init__(self, sql):
        """
        The __init__ function will call all the other functions in the class. The sql query is recieved as a parameter.
        """
        self.sql = sql
        self.create_connection()
        self.view_data()

    def create_connection(self):
        """
        Creates a connection to the predefined database.
        """
        self.conn = psycopg2.connect(host=self.hostname, user=self.username, password=self.password, dbname=self.database)
        self.cur = self.conn.cursor()

    def view_data(self):
        """
        This method tries to execute the sql query on the database and prints the results to the console.
        """
        try:
            self.cur.execute(self.sql)
            result = self.cur.fetchall()
            print("Query erzielte " + str(len(result)) + "Ergebnisse:")
            for r in result:
                print(r)
        except:
            print("Not a valid query.")
