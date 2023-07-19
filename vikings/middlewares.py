# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface


class CustomProxyMiddleware:
    def __init__(self):
        self.proxy = 'http://127.0.0.1:8080'

    def process_request(self, request, spider):
        if 'proxy' not in request.meta:
            request.meta['proxy'] = self.proxy

    def get_proxy(self):
        return self.proxy
