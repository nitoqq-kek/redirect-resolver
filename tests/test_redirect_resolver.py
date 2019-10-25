from operator import itemgetter

from aiohttp.test_utils import TestServer

from redirect_resolver.resolver import UrlResolver


async def test_resolver(server: TestServer):
    resolver = UrlResolver(max_workers=4)
    urls = [
        server.make_url("/self-redirect"),
        server.make_url("/cyclic-redirect1"),
        server.make_url("/infinite-content"),
        server.make_url("/large-content"),
        server.make_url("/content"),
        server.make_url("/redirect-to-content"),
        server.make_url("/redirect-with-large-body"),
    ]
    res = [i.dict(skip_defaults=True) async for i in resolver.resolve(map(str, urls))]
    assert sorted(res, key=itemgetter("url")) == [
        {
            "url": str(server.make_url("/content")),
            "real_url": str(server.make_url("/content")),
            "content_length": 12,
            "http_status": 200,
        },
        {"url": str(server.make_url("/cyclic-redirect1")), "error": "TooManyRedirects"},
        {
            "url": str(server.make_url("/infinite-content")),
            "real_url": str(server.make_url("/infinite-content")),
            "content_length": None,
            "http_status": 200,
        },
        {
            "url": str(server.make_url("/large-content")),
            "real_url": str(server.make_url("/large-content")),
            "content_length": 1073741824,
            "http_status": 200,
        },
        {
            "url": str(server.make_url("/redirect-to-content")),
            "real_url": str(server.make_url("/content")),
            "content_length": 12,
            "http_status": 200,
        },
        {
            "url": str(server.make_url("/redirect-with-large-body")),
            "real_url": str(server.make_url("/content")),
            "content_length": 12,
            "http_status": 200,
        },
        {"url": str(server.make_url("/self-redirect")), "error": "TooManyRedirects"},
    ]
