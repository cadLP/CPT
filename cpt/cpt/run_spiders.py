# -*- coding: utf-8 -*-
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from cpt.cpt.spiders.heise import HeiseSpider
from cpt.cpt.spiders.Wiwo import WiwoSpider
from cpt.cpt.spiders.sueddeutsche import SueddeutscheSpider
from cpt.cpt.spiders.FazSpider import FazSpider

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(HeiseSpider)
    yield runner.crawl(WiwoSpider)
    yield runner.crawl(SueddeutscheSpider)
    yield runner.crawl(FazSpider)
    reactor.stop()


crawl()
reactor.run()
