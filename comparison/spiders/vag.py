import re

import scrapy

from xlsx import load_input_data


class VagSpider(scrapy.Spider):
    name = "vag"
    allowed_domains = ["vag-ua.com"]
    start_urls = ["http://vag-ua.com/"]

    def start_requests(self):
        input_data = load_input_data()
        for index, data in enumerate(input_data, 1):
            code = data["code"]
            producer = data["producer"]
            url = f"{self.start_urls[0]}catalog-s-search-{code}"

            yield scrapy.Request(
                url, meta={"code": code, "producer": producer, "index": index}
            )

    def parse(self, response):
        code = response.meta["code"]
        producer = response.meta["producer"]
        index = response.meta["index"]
        catalog_items = response.css(".node--type-product")

        if len(catalog_items) == 0:
            self.logger.info("Item[%s] code %s is not in stock" % (index, code))
            yield {
                "code": code,
                "producer": producer,
                "quantity": 0,
                "is_available": False,
            }

        for item in catalog_items:
            availability = item.css(".form-radios label").get()
            if availability is not None:
                if "В наявності" in availability:
                    item_quantity = item.css(".in-stock::text").get()
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
