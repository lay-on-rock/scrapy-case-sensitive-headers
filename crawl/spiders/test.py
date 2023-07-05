import json
from scrapy.spiders import Spider
from scrapy.http import Request


from twisted.web.http_headers import Headers as TwistedHeaders

class Test(Spider):
    name = 'test'
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'aA': 'a',
            'Bb': 'b',
            'CC': 'c',
            'Content-Length': '14',
            'dD': 'd',
        },
    }
    
    # Preserve casing of headers
    TwistedHeaders._caseMappings[b'aa'] = b'aA'
    TwistedHeaders._caseMappings[b'bb'] = b'Bb'
    TwistedHeaders._caseMappings[b'cc'] = b'CC'
    TwistedHeaders._caseMappings[b'dd'] = b'dD'

    def start_requests(self):
        yield Request(
            'https://httpbin.org/post',
            body=json.dumps({'foo': 'bar'}),
            method='POST',
            # Sniff with Fiddler
            # meta={'proxy': 'https://127.0.0.1:8866'}
        )
    
    def parse(self, response): pass