from operator import attrgetter

from aiohttp.test_utils import TestServer

from redirect_resolver.resolver import UrlResolver, Result


async def test_resolver(server: TestServer):
    resolver = UrlResolver(max_workers=4, timeout=15)
    urls = [
        server.make_url("/self-redirect"),
        server.make_url("/cyclic-redirect1"),
        server.make_url("/infinite-content"),
        server.make_url("/large-content"),
        server.make_url("/content"),
        server.make_url("/redirect-to-content"),
        server.make_url("/redirect-with-large-body"),
        server.make_url("/infinite-non-cyclic-redirect"),
    ]
    res = [i async for i in resolver.resolve(map(str, urls))]

    assert sorted(res, key=attrgetter('url')) == sorted([
        Result(url=str(server.make_url('/infinite-content')), real_url=str(server.make_url('/infinite-content'))),
        Result(url=str(server.make_url('/large-content')), real_url=str(server.make_url('/large-content'))),
        Result(url=str(server.make_url('/self-redirect')), error='CyclicRedirect'),
        Result(url=str(server.make_url('/cyclic-redirect1')), error='CyclicRedirect'),
        Result(url=str(server.make_url('/redirect-with-large-body')), real_url=str(server.make_url('/content'))),
        Result(url=str(server.make_url('/content')), real_url=str(server.make_url('/content'))),
        Result(url=str(server.make_url('/redirect-to-content')), real_url=str(server.make_url('/content'))),
        Result(url=str(server.make_url('/infinite-non-cyclic-redirect')), error='TooManyRedirects'),
    ], key=attrgetter('url'))
