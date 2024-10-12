from datetime import datetime
from typing import Any
from urllib.parse import urlencode, urljoin

import scrapy

from xlsx import load_input_data


class QuattroSpider(scrapy.Spider):
    name = "quattro"
    allowed_domains = ["quattro.shop"]
    start_urls = ["https://quattro.shop/katalog/search/"]

    base_domain = "https://quattro.shop/"

    current_date = datetime.now()

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.input_data = load_input_data()

    def start_requests(self):
        for index, data in enumerate(self.input_data, 1):
            code = data["code"]
            producer = data["producer"]
            params = {"q": code}
            url = urljoin(self.start_urls[0], "?" + urlencode(params))
            yield scrapy.Request(
                url,
                errback=self.error_418_restart,
                cb_kwargs={"code": code, "producer": producer, "index": index},
            )

    def parse(self, response, code, producer, index):
        products = response.css(".catalogCard")

        if not products:
            self.logger.info("Item[%s] code %s is not in stock" % (index, code))
            yield {
                "code": code,
                "producer": producer,
                "quantity": 0,
                "is_available": False,
            }
        else:
            available_product = None
            for product in products:
                product_str = product.get()

                if code in product_str:
                    available_product = product
                    break

            if available_product:
                available_product_str = available_product.get()
                if "__grayscale" not in available_product_str:
                    available_product_uri = available_product.css(
                        ".catalogCard-title > a"
                    ).attrib["href"]
                    available_product_url = urljoin(
                        self.base_domain, available_product_uri
                    )

                    yield scrapy.Request(
                        url=available_product_url,
                        callback=self.parse_item,
                        errback=self.error_418_restart,
                        dont_filter=True,
                        cb_kwargs={"code": code, "producer": producer, "index": index},
                    )

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

    def parse_item(self, response, code, producer, index):
        product_purchase = int(
            response.css('meta[property="product:purchase_limit"]').attrib["content"]
        )

        self.logger.info(
            "Item[%s] code %s is in stock with %s quantity"
            % (index, code, product_purchase)
        )
        yield {
            "code": code,
            "producer": producer,
            "quantity": product_purchase,
            "is_available": True,
        }

    def error_418_restart(self, failure):
        request = failure.request
        yield request.copy()
