import re
from typing import Any

import scrapy

from xlsx import load_input_data


class AutovagSpider(scrapy.Spider):
    name = "autovag"
    allowed_domains = ["autovag.com.ua"]
    start_urls = ["http://autovag.com.ua"]

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.input_data = load_input_data()

    def parse(self, response):
        for index, data in enumerate(self.input_data, 1):
            code = data["code"]
            producer = data["producer"]

            yield scrapy.FormRequest(
                "http://autovag.com.ua/search",
                formdata={
                    "words": code,
                },
                callback=self.parse_products,
                errback=self.page_not_found,
                meta={"code": code, "producer": producer, "index": index},
            )

    def parse_products(self, response):
        code = response.meta["code"]
        producer = response.meta["producer"]
        index = response.meta["index"]

        product_lists = response.css(".list_table")
        if not product_lists:
            self.logger.info("Item[%s] Keyword %s is not in stock" % (index, code))
            return {
                "code": code,
                "producer": producer,
                "quantity": 0,
                "is_available": False,
            }

        product_list = product_lists[0]
        products = product_list.css("tr")
        products.pop(0)

        for product in products:
            product = product.get()

            if (
                re.search(rf"\b{re.escape(code)}\b", product)
                and "Под заказ" not in product
            ):
                self.logger.info("Item[%s] Keyword %s is in stock" % (index, code))
                return {
                    "code": code,
                    "producer": producer,
                    "quantity": 1,
                    "is_available": True,
                }

        self.logger.info("Item[%s] Keyword %s is not in stock" % (index, code))
        return {
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
