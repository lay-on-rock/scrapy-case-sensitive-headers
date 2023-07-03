"""Spider that logs request.headers.keys() & preserves header casing"""

from scrapy.spiders import Spider

# Ineffective strategy:
# Comes from: https://github.com/scrapy/scrapy/issues/5910,
#             https://github.com/scrapy/scrapy/issues/2711
# from twisted.web.http_headers import Headers as TwistedHeaders
# TwistedHeaders._caseMappings[b'chicken'] = b'CHICKEN'

from crawl.request import CaseSensitiveRequest

class Test(Spider):
    name = 'test'
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            # Test casing
            'lowercase': 'a',
            'mixOfLoWERanDUPPerCase': 'b',
            # Test order
            'CHICKEN': 'chicken',
            'EGG': 'egg',
        }
    }

    # DOES NOT WORK
    # start_urls = ['https://httpbin.org/headers']

    def start_requests(self):
        yield CaseSensitiveRequest('https://httpbin.org/headers')

    def parse(self, response):
        ## NOTE: Why is resposne from httpbin.org 
        self.logger.info(f"{response.request.headers.keys() = }")
        self.logger.info(f"{response.json() = }")