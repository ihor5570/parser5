import re

import scrapy

from xlsx import load_input_data


class SavatSpider(scrapy.Spider):
    name = "savat"
    allowed_domains = ["savat-auto.com.ua"]
    start_urls = ["http://savat-auto.com.ua/search/"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "comparison.middlewares.ProxyMiddleware": 610,
        },
        "RETRY_TIMES": 20,
    }

    def start_requests(self):
        input_data = load_input_data()
        for index, data in enumerate(input_data, 1):
            code = data["code"]
            producer = data["producer"]
            url = f"{self.start_urls[0]}{code}"

            yield scrapy.Request(
                url,
                meta={"code": code, "producer": producer, "index": index},
                errback=self.page_not_found,
            )

    def parse(self, response):
        code = response.meta["code"]
        producer = response.meta["producer"]
        index = response.meta["index"]
        catalog_items = response.css(".table-names table tbody tr")

        if len(catalog_items) == 0:
            self.logger.info("Item[%s] code %s is not in stock" % (index, code))
            yield {
                "code": code,
                "producer": producer,
                "quantity": 0,
                "is_available": False,
            }

        for item in catalog_items:
            availability = item.css('[aria-label="Термін доставки"] > b::text').get()
            if availability is not None:
                if "у наявності" in availability:
                    item_quantity = item.css('[aria-label="Наявність (шт)"]').get()
                    quantity = re.search(r"\d+", item_quantity).group()
                    self.logger.info(
                        "Item[%s] code %s is in stock with %s quantity"
                        % (index, code, quantity)
                    )
                    yield {
                        "code": code,
                        "producer": producer,
                        "quantity": int(quantity),
                        "is_available": True,
                    }
                    break
                else:
                    self.logger.info(
                        "Item[%s] code %s is in stock with %s quantity"
                        % (index, code, 0)
                    )
                    yield {
                        "code": code,
                        "producer": producer,
                        "quantity": 0,
                        "is_available": True,
                    }
            else:
                self.logger.info("Item[%s] code %s is not in stock" % (index, code))
                yield {
                    "code": code,
                    "producer": producer,
                    "quantity": 0,
                    "is_available": False,
                }

    def page_not_found(self, failure):
        request = failure.request
        code = request.meta["code"]
        producer = request.meta["producer"]
        index = request.meta["index"]

        self.logger.info("Item[%s] code %s is not in stock" % (index, code))

        yield {"code": code, "producer": producer, "quantity": 0, "is_available": False}
