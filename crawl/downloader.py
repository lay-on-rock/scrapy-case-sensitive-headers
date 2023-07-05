"""Inspired by: https://gist.github.com/pawelmhm/176a4d01aea93c65bd64155c761fcc7d"""

from collections import OrderedDict
from time import time
from scrapy.http import Headers
from twisted.web.iweb import UNKNOWN_LENGTH
from scrapy.core.downloader.handlers.http11 import ScrapyAgent, HTTP11DownloadHandler, _RequestBodyProducer
from twisted.web.http_headers import Headers as TxHeaders
from scrapy.utils.python import to_bytes, to_unicode
from urllib.parse import urldefrag, urlunparse

class OrderedHeaders(TxHeaders):

    def __init__(self, rawHeaders=None):
        self._rawHeaders = {}
        if rawHeaders is not None:
            for name, values in rawHeaders.items():
                self.setRawHeaders(name, values)
        # Sort request headers alphabetically
        self._rawHeaders = {key: value for key, value in sorted(self._rawHeaders.items())}
        print(self._rawHeaders)


class OrderedHeadersAgent(ScrapyAgent):

    def download_request(self, request):
        from twisted.internet import reactor

        timeout = request.meta.get("download_timeout") or self._connectTimeout
        agent = self._get_agent(request, timeout)

        # request details
        url = urldefrag(request.url)[0]
        method = to_bytes(request.method)
        headers = OrderedHeaders(request.headers)
        if isinstance(agent, self._TunnelingAgent):
            headers.removeHeader(b"Proxy-Authorization")
        if request.body:
            bodyproducer = _RequestBodyProducer(request.body)
        else:
            bodyproducer = None

        start_time = time()
        d = agent.request(
            method, to_bytes(url, encoding="ascii"), headers, bodyproducer
        )
        # set download latency
        d.addCallback(self._cb_latency, request, start_time)
        # response body is ready to be consumed
        d.addCallback(self._cb_bodyready, request)
        d.addCallback(self._cb_bodydone, request, url)
        # check download timeout
        self._timeout_cl = reactor.callLater(timeout, d.cancel)
        d.addBoth(self._cb_timeout, request, url, timeout)
        return d


class AlphabeticallyOrderHeadersDownloader(HTTP11DownloadHandler):
    def download_request(self, request, spider):
        """Return a deferred for the HTTP download"""
        agent = OrderedHeadersAgent(
            contextFactory=self._contextFactory,
            pool=self._pool,
            maxsize=getattr(spider, "download_maxsize", self._default_maxsize),
            warnsize=getattr(spider, "download_warnsize", self._default_warnsize),
            fail_on_dataloss=self._fail_on_dataloss,
            crawler=self._crawler,
        )
        return agent.download_request(request)
