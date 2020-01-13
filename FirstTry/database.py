import psycopg2

hostname = "localhost"
username = "postgres"
password = "2522"
database = "NewspaperCrawler"

def queryCrawler(conn):
    cur = conn.cursor()
    cur.execute("""Select * from newspaper_metadata""")
    rows = cur.fetchall()

    for row in rows:
        print(row)

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
queryCrawler(conn)
conn.close()