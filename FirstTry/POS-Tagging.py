import psycopg2
import treetaggerwrapper
import de_core_news_sm


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
class CrawlerTagging:
    """
    This class will call the different tagging methods that are available.
    The options are CrawlerTagging("TreeTagger"), CrawlerTagging("Spacy POS") and CrawlerTagging("Spacy NER").
    """

    def __init__(self, tagging_method=[], *args, **kwargs):
        """
        The __init__ function will call all the other functions in the class. Depending on which tagging_method is
        added it will select the corresponding function.

        :param tagging_method: Selection which Tagging Method should be called.
        :type tagging_method: string
        """
        super(CrawlerTagging, self).__init__(*args, **kwargs)
        self.create_connection()
        self.get_texts()
        for arg in tagging_method:
            if arg == "TreeTagger":
                self.treetagger_pos()
            elif arg == "Spacy POS":
                self.spacy_pos()
            elif arg == "Spacy NER":
                self.spacy_ner()

    def create_connection(self):
        """
        Creates a connection to the predefined database.
        """
        self.conn = psycopg2.connect(host="localhost", user="postgres", password="2522", dbname="NewspaperCrawler")
        self.cur = self.conn.cursor()

    def get_texts(self):
        """
        Getting all the scraped newspaper articles from the database.

        """
        self.cur.execute("""SELECT * FROM text;""")
        self.results = self.cur.fetchall()

    def treetagger_pos(self):
        """
        Tagging the texts using the German POS Tagger from TreeTagger. And writing it back into the database.
        """
        self.cur.execute("""INSERT INTO method (description, id) VALUES ('TreeTagger_POS', '1') ON CONFLICT DO NOTHING;""")
        self.conn.commit()

        tagger = treetaggerwrapper.TreeTagger(TAGLANG='de', TAGDIR='../Treetagger')

        for a, b in self.results:
            sql="""SELECT * FROM pos WHERE method_id='1' AND metadaten_id='"""+str(b)+"""';"""
            self.cur.execute(sql)
            if self.cur.fetchall() is None:
                tags = tagger.tag_text(a)
                sql = """INSERT INTO pos (pos_tags, method_id, metadaten_id) VALUES (%s, '1', %s);"""
                data = (tags, b)
                self.cur.execute(sql, data)
                self.conn.commit()

    def spacy_pos(self):
        """
        Tagging the texts using the German POS Tagger from Spacy. And writing it back into the database.
        """
        self.cur.execute("""INSERT INTO method (description, id) VALUES ('Spacy_POS', '2') ON CONFLICT DO NOTHING;""")
        self.conn.commit()

        nlp = de_core_news_sm.load()

        for a, b in self.results:
            sql = """SELECT * FROM pos WHERE method_id='2' AND metadaten_id='""" + str(
                b) + """';"""
            self.cur.execute(sql)
            if self.cur.fetchall() is None:
                doc = nlp(a)
                tags = ' '.join('{word}/{tag}'.format(word=t.orth_, tag=t.tag_) for t in doc)
                sql = """INSERT INTO pos (pos_tags, method_id, metadaten_id) VALUES (%s, '2', %s)"""
                data = (tags, b)
                self.cur.execute(sql, data)
                self.conn.commit()

    def spacy_ner(self):
        """
        Getting Named Entities using NER from Spacy. And writing it back into the database.
        """
        self.cur.execute("""INSERT INTO method (description, id) VALUES ('Spacy_NER', '3') ON CONFLICT DO NOTHING;""")
        self.conn.commit()

        nlp = de_core_news_sm.load()

        for a, b in self.results:
            sql = """SELECT * FROM pos WHERE method_id='3' AND metadaten_id='""" + str(
                b) + """';"""
            self.cur.execute(sql)
            if self.cur.fetchall() is None:
                doc = nlp(a)
                tags = []
                for ent in doc.ents:
                    tags.append(ent.text + '/' + ent.label_)

                sql = """INSERT INTO ner (ner_tags, method_id, metadaten_id) VALUES (%s, '3', %s)"""
                data = (tags, b)
                self.cur.execute(sql, data)
                self.conn.commit()

# TreeTagger, Spacy POS, Spacy NER
CrawlerTagging(["TreeTagger", "Spacy POS"])
