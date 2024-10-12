class ProxyMiddleware:
    def __init__(self, proxy):
        self.proxy = proxy

    @classmethod
    def from_crawler(cls, crawler):
        return cls(proxy=crawler.settings.get("PROXY_URL"))

    def process_request(self, request, spider):
        if self.proxy:
            request.meta["proxy"] = self.proxy
