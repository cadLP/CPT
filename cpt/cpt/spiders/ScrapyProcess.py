from twisted.internet import reactor, defer, error
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import sys
from cpt.spiders.sueddeutsche import SueddeutscheSpider
from cpt.spiders.FAZSpider import FazSpider
from cpt.spiders.Wiwo import WiwoSpider

from scrapy.settings import Settings
from cpt import settings as cptssettings
from scrapy.crawler import CrawlerProcess
from threading import Thread

"""Test, ob ich den Reaktor neugestartet bekomme"""

crawler_settings = Settings()
crawler_settings.setmodule(cptssettings)

#configure_logging()
#runner = CrawlerRunner(settings=crawler_settings)
allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                     "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
testcategories = ["Wissen"]


class ScrapyProcess:
    crawler_settings = Settings()
    crawler_settings.setmodule(cptssettings)


    allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                     "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
    testcategories = ["Wissen"]
    spiders = []
    categories = []

    def __init__(self, cat_list=[], spider_list=[]):
        for cat in cat_list:
            if cat in allcategories:
                self.categories.append(cat)
        for spider in spider_list:
            self.spiders.append(spider)

    def runcrawler(self):
        self.startcrawl()


    def startcrawl(self):
        process = CrawlerProcess(settings=crawler_settings)
        if "sueddeutsche" in self.spiders:
            process.crawl(SueddeutscheSpider(cat_list=self.categories))
        if "faz" in self.spiders:
            process.crawl(FazSpider(cat_list=self.categories))
        if "wiwo" in self.spiders:
            process.crawl(WiwoSpider(cat_list=self.categories))
        Thread(target=process.start).start()