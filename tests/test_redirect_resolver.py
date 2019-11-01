import pytest
from aiohttp.test_utils import TestServer

from redirect_resolver.resolver import ResolveError, resolve_url


@pytest.mark.parametrize('url,expected_url', [
    ('/infinite-content', '/infinite-content'),
    ('/large-content', '/large-content'),
    ('/redirect-with-large-body', '/content'),
    ('/content', '/content'),
    ('/redirect-to-content', '/content'),
])
async def test_resolver(server: TestServer, url, expected_url):
    url = server.make_url(url)
    real_url = await resolve_url(str(url))
    assert real_url == server.make_url(expected_url)


@pytest.mark.parametrize('url', [
    '/self-redirect',
    '/cyclic-redirect1',
    '/infinite-non-cyclic-redirect',
])
async def test_resolver_error(server: TestServer, url):
    url = server.make_url(url)
    with pytest.raises(ResolveError):
        await resolve_url(str(url))
