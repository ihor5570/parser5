BOT_NAME = "comparison"

SPIDER_MODULES = ["comparison.spiders"]
NEWSPIDER_MODULE = "comparison.spiders"

LOG_LEVEL = "INFO"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 0

ITEM_PIPELINES = {
    "comparison.pipelines.ComparisonPipeline": 300,
}

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0"
