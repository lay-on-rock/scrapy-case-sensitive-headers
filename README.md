### Scrapy case senstive, alphabetically-ordered headers

#### Project start
```bash
pip install -r requirements/dev.txt
# OPTIONAL: If you also want to order Content-Length in the request headers,
# Modify site package
# => twisted/web/_newclient.py
# Change lines 787-790 from 
# self._writeHeaders(transport, networkString("Content-Length": ...))
# to: 
# self._writeHeaders(transport, None)
scrapy crawl test
```

----

#### Project motivations

It is true that [section 3.2.2 of the RFC Standard for HTTP/1.1 protocol](https://www.rfc-editor.org/rfc/rfc7230#section-3.2.2) states that header sequencing and casing is insignificant. So, if this problem exists for you, it means a server has been customized to reject RFC standards. That being said, if you have reason to believe that header order is leading to anti-bot, this might be worth something to try.

Before doing this, you can consider:
- proxy rotation, user-agent rotation, spoofing headers/cookies;
- `DOWNLOADER_CLIENT_TLS_METHOD=TLSv1.2` [as per Scrapy #4951](https://github.com/scrapy/scrapy/issues/4951);
- Check if request if HTTP/2 (h2), if so can try [using HTTP/2 in Scrapy](https://docs.scrapy.org/en/latest/topics/settings.html#download-handlers-base)

If this doesn't work, you can turn to other modules:
- [curl_cffi](https://github.com/yifeikong/curl_cffi), `curl-impersonate` in python, to impersonate browsers' TLS signatures or JA3 fingerprints (see reading on [TLS fingerprinting](https://lwthiker.com/networks/2022/06/17/tls-fingerprinting.html), [HTTP/2 fingerprinting](https://lwthiker.com/networks/2022/06/17/http2-fingerprinting.html));
- asynchronous requests, something like this code snippet:
    ```python
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    # How many threads are you comfortable with?
    THREAD_POOL = 8

    session = requests.Session()
    # Use this adapter instead, for ordered headers
    # class SortedHTTPAdapter(requests.adapters.HTTPAdapter):
    # def add_headers(self, request, **kwargs):
    #     request.headers = collections.OrderedDict(
    #         ((key, value) for key, value in sorted(request.headers.items()))
    #     )
    session.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=THREAD_POOL, max_retries=3, pool_block=True))

    def post(url):
        """Function used to make request"""
        return session.post(url, ...)

    def download(urls):
        start = datetime.now()
        with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
            for response in list(executor.map(post, urls)):
                if 500 <= response.status_code <= 600:
                    # Server overload, wait
                    time.sleep(5)
        duration = datetime.now() - start
        duration_seconds = duration.total_seconds()
        print(f"Completed in {duration_seconds = }")
    
    download(['url1', 'url2', '...'])
    ```
- [httpx](https://github.com/encode/httpx) to make HTTP/2 request;

#### Project summary

Scrapy natively formats headers.
```python
import scrapy
scrapy.http.Headers({'caCHE-conTROL': 'test'})
# ['Cache-Control']
```

Anti-bot can potentially be case senstive in headers.
References:
- [A situation where someone needed a case sensitive header, Scrapy #5910](https://github.com/scrapy/scrapy/issues/5910)

To handle case sensitivity, this spider uses `_caseMappings` attribute from Twisted internal headers class:
```python
# Declare before request or spider declaration
from twisted.web.http_headers import Headers as TwistedHeaders
TwistedHeaders._caseMappings[b'cache-control'] = b'caCHE-conTROL'
```
References:
- [Scrapy capitalizes headers for request, Scrapy #2711](https://github.com/scrapy/scrapy/issues/2711)

#### Current issues

- It is a lot of work to modify the twisted code itself to make content-length header respect order, there should be an easier work-around to that

----