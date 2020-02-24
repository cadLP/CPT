from twisted.internet import reactor, defer, error
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from cpt.cpt.spiders.sueddeutsche import SueddeutscheSpider
from cpt.cpt.spiders.FazSpider import FazSpider
from cpt.cpt.spiders.Wiwo import WiwoSpider
from cpt.cpt.spiders.heise import HeiseSpider
from cpt.cpt.spiders.spiegel_spider import SpiegelSpider
from scrapy.settings import Settings
from cpt.cpt import settings as cptsettings


class ScrapyCrawler:
    crawler_settings = Settings()
    crawler_settings.setmodule(cptsettings)
    configure_logging()
    runner = CrawlerRunner(settings=crawler_settings)

    allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                     "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
    spiders = []
    categories = []

    def __init__(self, cat_list=[], spider_list=[]):
        for cat in cat_list:
            if cat in self.allcategories:
                self.categories.append(cat)
        for spider in spider_list:
            self.spiders.append(spider)

    def runcrawler(self):
        self.startcrawl()


    @defer.inlineCallbacks
    def crawl(self):
        if "sueddeutsche" in self.spiders:
            yield self.runner.crawl(SueddeutscheSpider(cat_list=self.categories))
        if "faz" in self.spiders:
            yield self.runner.crawl(FazSpider(cat_list=self.categories))
        if "wiwo" in self.spiders:
            yield self.runner.crawl(WiwoSpider(cat_list=self.categories))
        if "heise" in self.spiders:
            yield self.runner.crawl(HeiseSpider(cat_list=self.categories))
        if "spiegel" in self.spiders:
            yield self.runner.crawl(SpiegelSpider(cat_list=self.categories))
        reactor.stop()

    def startcrawl(self):
        try:
            self.crawl()
        except:
            pass
        reactor.run()

