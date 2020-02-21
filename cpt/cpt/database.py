import psycopg2

hostname = "localhost"
username = "crawler"
password = "test"
database = "crawler"


conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cur = conn.cursor()
cur.execute("""Insert into metadaten (title, date_retrieved, date_published, url, id, authors, category, source) values ('Titel', current_date, '20.06.2020', 'URL', default, 'Author', 'category', 'FAZ')""")
conn.commit()
conn.close()