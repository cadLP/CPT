from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from CPT.cpt.cpt.spiders.Wiwo import WiwoSpider
from scrapy.settings import Settings
from CPT.cpt.cpt import settings as cptsettings

crawler_settings = Settings()
crawler_settings.setmodule(cptsettings)
configure_logging()
runner = CrawlerRunner(settings=crawler_settings)
allcategories = ["Politik", "Wirtschaft", "Gesellschaft", "Technik", "IT", "Wissen", "Karriere"]
testcategories = ["IT"]


@defer.inlineCallbacks
def crawl():

    yield runner.crawl(WiwoSpider(cat_list=testcategories))
    # yield runner.crawl(WiwoSpider)
    #reactor.stop()
    runner.join()
crawl()
reactor.run()