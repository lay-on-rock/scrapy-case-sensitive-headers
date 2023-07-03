"""
Case sensitive headers, does not call key.title() in normkey method
SOURCE: https://github.com/scrapy/scrapy/blob/master/scrapy/utils/datatypes.py#L20C1-L83C56
"""

from scrapy.http.headers import Headers

class CaseSensitiveHeaders(Headers):
    """Case insensitive http headers dictionary"""

    def normkey(self, key):
        """Normalize key to bytes"""
        # SOURCE:
        # return self._tobytes(key.title())
        # MODIFIED:
        return self._tobytes(key)