from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from comparison.spiders.autovag import AutovagSpider
from comparison.spiders.bestparts import BestpartsSpider
from comparison.spiders.quattro import QuattroSpider
from comparison.spiders.savat import SavatSpider
from comparison.spiders.vag import VagSpider


def start_scraping() -> None:
    """
    Setups scrapers' settings and starts them
    """

    process = CrawlerProcess(get_project_settings())

    process.crawl(BestpartsSpider)
    process.crawl(SavatSpider)
    process.crawl(VagSpider)
    process.crawl(QuattroSpider)
    process.crawl(AutovagSpider)

    process.start()
