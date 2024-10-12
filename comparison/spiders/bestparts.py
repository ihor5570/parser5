import scrapy

from xlsx import load_input_data


class BestpartsSpider(scrapy.Spider):
    name = "bestparts"
    allowed_domains = ["bestparts.kiev.ua"]
    start_urls = [
        "https://bestparts.kiev.ua",
        "https://bestparts.kiev.ua/catalog/search/",
    ]

    def start_requests(self):
        input_data = load_input_data()
        for index, data in enumerate(input_data, 1):
            code = data["code"]
            producer = data["producer"]
            url = f"{self.start_urls[1]}?q={code}"

            yield scrapy.Request(
                url,
                meta={"code": code, "producer": producer, "index": index},
                callback=self.parse_catalog,
                errback=self.error_418_restart,
                dont_filter=True,
            )

    def parse_catalog(self, response):
        code = response.meta["code"]
        producer = response.meta["producer"]
        index = response.meta["index"]
        catalog_items = response.css(".catalog-grid__item")

        if len(catalog_items) == 0:
            self.logger.info("Item[%s] code %s is not in stock" % (index, code))
            yield {
                "code": code,
                "producer": producer,
                "quantity": 0,
                "is_available": False,
            }
        else:
            item = catalog_items[0]
            availability = item.css(".catalogCard-availability::text").get().strip()
            if availability == "В наличии":
                item_url = item.css(".catalogCard-title > a").attrib["href"]
                item_url = f"{self.start_urls[0]}{item_url}"

                yield scrapy.Request(
                    url=item_url,
                    meta=response.meta,
                    callback=self.parse_item,
                    errback=self.error_418_restart,
                    dont_filter=True,
                )
            else:
                self.logger.info("Item[%s] code %s is in stock with %s quantity" % (index, code, 0))
                yield {
                    "code": code,
                    "producer": producer,
                    "quantity": 0,
                    "is_available": True,
                }

    def parse_item(self, response):
        code = response.meta["code"]
        producer = response.meta["producer"]
        index = response.meta["index"]

        item_max_quantity = response.css(
            'meta[property="product:purchase_limit"]'
        ).attrib["content"]

        self.logger.info("Item[%s] code %s is in stock with %s quantity" % (index, code, item_max_quantity))
        yield {
            "code": code,
            "producer": producer,
            "quantity": int(item_max_quantity),
            "is_available": True,
        }

    def error_418_restart(self, failure):
        request = failure.request
        yield request.copy()

