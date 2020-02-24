from twisted.internet import reactor, defer, error
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from cpt.spiders.sueddeutsche import SueddeutscheSpider
from cpt.spiders.FAZSpider import FazSpider
from cpt.spiders.Wiwo import WiwoSpider
from cpt.spiders.heise import HeiseSpider
from cpt.spiders.spiegel_spider import SpiegelSpider
from scrapy.settings import Settings
from cpt import settings as cptsettings


class ScrapyCrawler:
    """
    This class is used to properly create and start the selected spiders.
    """
    crawler_settings = Settings()
    crawler_settings.setmodule(cptsettings)
    configure_logging()
    runner = CrawlerRunner(settings=crawler_settings)

    allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                     "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
    spiders = []
    categories = []

    def __init__(self, cat_list=[], spider_list=[]):
        """
        This method creates a Scrapycrawler from a list of selected spiders and categories.
        :param cat_list:
        :param spider_list:
        """
        for cat in cat_list:
            if cat in self.allcategories:
                self.categories.append(cat)
        for spider in spider_list:
            self.spiders.append(spider)

    @defer.inlineCallbacks
    def crawl(self):
        """
        This method crawls all selected spiders in sequence over selected categories.
        :return:
        """
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
        """
        This method starts the crawling process and the associated Twisted Internet Reactor.
        :return:
        """
        try:
            self.crawl()
        except:
            pass
        reactor.run()
