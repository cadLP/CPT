import psycopg2
import treetaggerwrapper
import pprint
import de_core_news_sm

#pipeline datenbank anpassen, dogstring

# hostname = "localhost"
# username = "postgres"
# password = "2522"
# database = "NewspaperCrawler"
#
# conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
# cur = conn.cursor()

# cur.execute("""INSERT INTO method (description, id)
#             VALUES ('method_1', '001')""")
# conn.commit()
#
# tagger = treetaggerwrapper.TreeTagger(TAGLANG='de', TAGDIR='../Treetagger')
#
# cur.execute("""SELECT * FROM text;""")
# results = cur.fetchall()
class CrawlerTagging():

    def __init__(self, tagging_method):
        self.tagging_method = tagging_method
        self.create_connection()
        self.get_texts()
        if self.tagging_method is "TreeTagger":
            self.treetagger_pos()
        elif self.tagging_method is "Spacy POS":
            self.spacy_pos()
        elif self.tagging_method is "Spacy NER":
            self.spacy_ner()

    def create_connection(self):
        self.conn = psycopg2.connect(host="localhost", user="postgres", password="2522", dbname="NewspaperCrawler")
        self.cur = self.conn.cursor()

    def get_texts(self):
        self.cur.execute("""SELECT * FROM text;""")
        self.results = self.cur.fetchall()

    def treetagger_pos(self):
        self.cur.execute("""INSERT INTO method (description, id) VALUES ('TreeTagger_POS', '1') ON CONFLICT DO NOTHING;""")
        self.conn.commit()

        tagger = treetaggerwrapper.TreeTagger(TAGLANG='de', TAGDIR='../Treetagger')

        for a, b in self.results:
            tags = tagger.tag_text(a)
            sql = """INSERT INTO pos (pos_tags, method_id, metadaten_id) VALUES (%s, '1', %s);"""
            data = (tags, b)
            self.cur.execute(sql, data)
            self.conn.commit()

    def spacy_pos(self):
        self.cur.execute("""INSERT INTO method (description, id) VALUES ('Spacy_POS', '2') ON CONFLICT DO NOTHING;""")
        self.conn.commit()

        nlp = de_core_news_sm.load()

        for a, b in self.results:
            doc = nlp(a)
            tags = ' '.join('{word}/{tag}'.format(word=t.orth_, tag=t.tag_) for t in doc)

            sql = """INSERT INTO pos (pos_tags, method_id, metadaten_id) VALUES (%s, '2', %s)"""
            data = (tags, b)
            self.cur.execute(sql, data)
            self.conn.commit()

    def spacy_ner(self):
        self.cur.execute("""INSERT INTO method (description, id) VALUES ('Spacy_NER', '3') ON CONFLICT DO NOTHING;""")
        self.conn.commit()

        nlp = de_core_news_sm.load()

        for a, b in self.results:
            doc = nlp(a)

            tags = []

            for ent in doc.ents:
                tags.append(ent.text + '/' + ent.label_)

            sql = """INSERT INTO ner (ner_tags, method_id, metadaten_id) VALUES (%s, '3', %s)"""
            data = (tags, b)
            self.cur.execute(sql, data)
            self.conn.commit()

# TreeTagger, Spacy POS, Spacy NER
CrawlerTagging("TreeTagger")
