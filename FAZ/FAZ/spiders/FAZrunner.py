# from twisted.internet import reactor, defer
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging
# from scrapy.settings import Settings
# from FAZ.FAZ import settings as cptssettings
# from FAZ.FAZ.spiders.FAZSpider import FazSpider
#
#
# crawler_settings = Settings()
# crawler_settings.setmodule(cptssettings)
# configure_logging()
# runner = CrawlerRunner(settings=crawler_settings)
# allcategories = ["Politik", "Wirtschaft", "Finanzen", "Sport", "Kultur", "Gesellschaft", "Reisen", "Digital", "Technik",
#                 "Meinung", "Wissen", "Regional", "Karriere"]
# testcategories = ["Politik", "Meinung"]
# @defer.inlineCallbacks
# def crawl():
#
#     #yield runner.crawl(SueddeutscheSpider(categories=testcategories))
#     yield runner.crawl(FazSpider(cat_list=testcategories))
#     reactor.stop()
#
# crawl()
# reactor.run()

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from FAZ.FAZ.spiders.FAZSpider import FazSpider
from scrapy.settings import Settings
from FAZ.FAZ import settings as cptssettings

crawler_settings = Settings()
crawler_settings.setmodule(cptssettings)
configure_logging()
runner = CrawlerRunner(settings=crawler_settings)
allcategories = ["Sport", "Politik", "Wirtschaft", "Meinung", "Regional", "Kultur", "Gesellschaft",
                     "Wissen", "Digital", "Karriere", "Reisen", "Technik"]
testcategories = ["Politik"]


@defer.inlineCallbacks
def crawl():

    yield runner.crawl(FazSpider(cat_list=testcategories))
    # yield runner.crawl(SueddeutscheSpider)
    #reactor.stop()
    runner.join()
crawl()
reactor.run()