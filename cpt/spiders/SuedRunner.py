from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from cpt.spiders.sueddeutsche import SueddeutscheSpider
from cpt.spiders.FAZSpider import FazSpider
from scrapy.settings import Settings
from cpt import settings as cptssettings

crawler_settings = Settings()
crawler_settings.setmodule(cptssettings)

configure_logging()
runner = CrawlerRunner(settings=crawler_settings)
allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                     "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
testcategories = ["Sport"]


@defer.inlineCallbacks
def crawl():

    yield runner.crawl(SueddeutscheSpider(cat_list=testcategories))
    #yield runner.crawl(SueddeutscheSpider)
    yield runner.crawl(FazSpider(cat_list=testcategories))
    reactor.stop()
    #runner.join()
crawl()
reactor.run()
