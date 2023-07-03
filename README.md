### Scrapy case senstive headers (in development)

#### Project start
```bash
pip install -r requirements/dev.txt
scrapy crawl test
# Expected output:
... [test] INFO: response.request.headers.keys() = dict_keys([b'lowercase', b'mixOfLoWERanDUPPerCase', b'CHICKEN', b'EGG', b'User-Agent', b'Accept-Encoding'])
... [test] INFO: response.json() = {'headers': {'Accept-Encoding': 'gzip, deflate', 'Chicken': 'chicken', 'Egg': 'egg', 'Host': 'httpbin.org', 'Lowercase': 'a', 'Mixofloweranduppercase': 'b', 'User-Agent': 'Scrapy/2.9.0 (+https://scrapy.org)', 'X-Amzn-Trace-Id': '...'}}
```

----

#### Project motivations

Scrapy natively formats headers.
```python
import scrapy
scrapy.http.Headers({'caCHE-conTROL': 'test'})
# ['Cache-Control']
```

Anti-bot can potentially be case senstive in headers.
References:
- [A situation where someone needed a case sensitive header Scrapy #5910](https://github.com/scrapy/scrapy/issues/5910)

A suggested strategy is to modify `_caseMappings` attribute from Twisted internal headers class:
```python
# Declare before request or spider declaration
from twisted.web.http_headers import Headers as TwistedHeaders
TwistedHeaders._caseMappings[b'cache-control'] = b'caCHE-conTROL'
```
References:
- [Scrapy capitalizes headers for request, Scrapy #2711](https://github.com/scrapy/scrapy/issues/2711)

As scrapy wraps this is `Headers` class, this normalizes keys via a `normkey` function. This function calls `.title()` method.

```python
# https://github.com/scrapy/scrapy/blob/master/scrapy/http/headers.py
class Headers(CaselessDict):
    ...
    def normkey(self, key):
        """Normalize key to bytes"""
        return self._tobytes(key.title())
```

To support case sensitive header functionality, we can create a custom scrapy `Request` class that does not use `Headers()` but a custom `Headers` class that removes the title method from being called.

For example:

```python
yield CaseSensitiveRequest(
    url='https://httpbin.org/headers',
    headers={
        # Test casing
        'lowercase': 'a',
        'mixOfLoWERanDUPPerCase': 'b',
        'CHICKEN': 'chicken',
        'EGG': 'egg',
    },
)
```

**This does not work with `start_urls`. You must use `start_requests`.** This is because (I think) `start_urls` will instantiate `Request` object, not the customized `CaseSensitiveRequest`.

----

#### Questions

- Can this support ordered headers?
- Why does `https://httpbin.org/headers` not return case sensitive headers, but `response.request.headers.keys()` does?