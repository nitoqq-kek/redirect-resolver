from __future__ import annotations

import typing as t

import aiohttp
from aiohttp import InvalidURL, hdrs
from yarl import URL


def get_redirect_url(resp) -> t.Optional[URL]:
    url = resp.url
    r_url = (resp.headers.get(hdrs.LOCATION) or
             resp.headers.get(hdrs.URI))
    if r_url is None:
        return

    try:
        r_url = URL(r_url, encoded=False)

    except ValueError:
        raise InvalidURL(r_url)

    scheme = r_url.scheme
    if scheme not in ('http', 'https', ''):
        raise InvalidURL(r_url)
    elif not scheme:
        r_url = url.join(r_url)

    return r_url


class ResolveError(Exception):
    pass


async def resolve_url(url: str, max_redirects=10, timeout=20) -> URL:
    url = URL(url)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        history = set()
        redirect_count = 0
        while True:
            if redirect_count == max_redirects:
                raise ResolveError('Too many redirects')
            async with session.get(url, allow_redirects=False) as resp:
                if resp.status in (301, 302, 303, 307, 308):
                    next_url = get_redirect_url(resp)
                    if next_url in history:
                        raise ResolveError('Cyclic redirect')
                    history.add(url)
                    redirect_count += 1
                    url = next_url
                    continue
                else:
                    return resp.real_url
