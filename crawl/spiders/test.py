import json
from scrapy.spiders import Spider
from scrapy.http import Request


from twisted.web.http_headers import Headers as TwistedHeaders

class Test(Spider):
    name = 'test'
    request_body = {'foo': 'bar'}
    custom_settings = {
        'DOWNLOAD_HANDLERS_BASE': {
            'https': 'crawl.downloader.AlphabeticallyOrderHeadersDownloader',
        },
        'DEFAULT_REQUEST_HEADERS': {
            'aA': 'a',
            'Bb': 'b',
            'CC': 'c',
            ## NOTE: To prevent Twisted from auto-populating Content-Length
            ## @ the start of request headers, please change in site-packages:
            ## twisted/web/_newclient.py lines 787-790
            # https://github.com/twisted/twisted/blob/trunk/src/twisted/web/_newclient.py#L779C1-L790C10
            # self._writeHeaders(
            #     transport,
            #     networkString("Content-Length: %d\r\n" % (self.bodyProducer.length,)),
            # )
            # to => 
            # self._writeHeaders(transport, None)
            'Content-Length': len(bytes(str(request_body).encode())),
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
            body=json.dumps(self.request_body),
            method='POST',
            # Sniff with Fiddler
            # meta={'proxy': 'https://127.0.0.1:8866'}
        )
    
    def parse(self, response): self.logger.info(response.json())