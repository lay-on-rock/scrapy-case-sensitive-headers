"""
Request that calls CaseSensitiveHeaders as opposed to Headers object
SOURCE: https://github.com/scrapy/scrapy/blob/master/scrapy/http/request/__init__.py#L47C1-L114C58
"""

from scrapy.http.request import Request
# SOURCE:
# from scrapy.http.headers import Headers
# MODIFIED:
from crawl.headers import CaseSensitiveHeaders

from typing import Optional, Callable, Union, List


class CaseSensitiveRequest(Request):
    def __init__(
        self,
        url: str,
        callback: Optional[Callable] = None,
        method: str = "GET",
        headers: Optional[dict] = None,
        body: Optional[Union[bytes, str]] = None,
        cookies: Optional[Union[dict, List[dict]]] = None,
        meta: Optional[dict] = None,
        encoding: str = "utf-8",
        priority: int = 0,
        dont_filter: bool = False,
        errback: Optional[Callable] = None,
        flags: Optional[List[str]] = None,
        cb_kwargs: Optional[dict] = None,
    ) -> None:
        self._encoding = encoding  # this one has to be set first
        self.method = str(method).upper()
        self._set_url(url)
        self._set_body(body)
        if not isinstance(priority, int):
            raise TypeError(f"Request priority not an integer: {priority!r}")
        self.priority = priority

        if not (callable(callback) or callback is None):
            raise TypeError(
                f"callback must be a callable, got {type(callback).__name__}"
            )
        if not (callable(errback) or errback is None):
            raise TypeError(f"errback must be a callable, got {type(errback).__name__}")
        self.callback = callback
        self.errback = errback

        self.cookies = cookies or {}
        # SOURCE:
        # self.headers = Headers(headers or {}, encoding=encoding)
        # MODIFIED:
        self.headers = CaseSensitiveHeaders(headers or {}, encoding=encoding)

        self.dont_filter = dont_filter

        self._meta = dict(meta) if meta else None
        self._cb_kwargs = dict(cb_kwargs) if cb_kwargs else None
        self.flags = [] if flags is None else list(flags)