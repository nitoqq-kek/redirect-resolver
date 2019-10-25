from __future__ import annotations

import asyncio
import logging
import typing as t

import aiohttp
import pydantic
from aiohttp import InvalidURL, hdrs
from yarl import URL

log = logging.getLogger(__name__)


class Result(pydantic.BaseModel):
    url: str
    real_url: t.Optional[str]
    error: t.Optional[str]


class Node:
    def __init__(self, value: URL, next_node: Node = None):
        self.value = value
        self.next = next_node

    def __repr__(self):
        return "Node <{}>".format(self.value)


def has_cycle(head: Node) -> bool:
    """Floyd's Cycle-Finding Algorithm"""

    slow, fast = head, head

    while fast is not None and fast.next is not None:
        slow, fast = slow.next, fast.next.next

        if slow == fast:
            return True

    return False


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


class UrlResolver:
    def __init__(self, max_workers=100, timeout=60, max_redirects=10):
        self._timeout = timeout
        self._max_redirects = max_redirects
        self._max_workers = max_workers
        self._input_queue = asyncio.Queue(maxsize=max_workers * 100)
        self._output_queue = asyncio.Queue(maxsize=max_workers * 100)

    async def resolve_url(self, start_url: str):
        url = URL(start_url)
        log.debug("Processing URL: %s", url)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self._timeout)) as session:
            history = Node(url)
            last_node = history
            node_index = {url: last_node}

            redirect_count = 0
            while True:
                if redirect_count == self._max_redirects:
                    return Result(
                        url=start_url,
                        error="TooManyRedirects"
                    )
                try:
                    async with session.get(url, allow_redirects=True, max_redirects=1) as resp:
                        return Result(
                            url=start_url,
                            real_url=str(resp.real_url),
                        )
                except aiohttp.TooManyRedirects as e:
                    resp = e.history[0]
                    next_url = get_redirect_url(resp)
                    node_index.setdefault(next_url, Node(next_url))
                    node = node_index[next_url]
                    last_node.next = node
                    last_node = node
                    if has_cycle(history):
                        return Result(
                            url=start_url,
                            error="CyclicRedirect"
                        )
                    url = next_url
                    redirect_count += 1
                except Exception as e:
                    return Result(
                        url=start_url,
                        error=f"{e.__class__.__name__}"
                    )

    async def worker(self):
        while True:
            try:
                url = await self._input_queue.get()
            except asyncio.CancelledError:
                log.debug("Worker finished")
                break
            else:
                try:
                    log.debug("Processing URL: %s", url)
                    result = await self.resolve_url(url)
                    await self._output_queue.put(result)
                except Exception:
                    log.exception("Unhandled exception")
                finally:
                    self._input_queue.task_done()
                    log.debug("Finished processing URL: %s", url)

    async def put_urls(self, urls: t.Union[t.AsyncIterable, t.Iterable]):
        async def _put(url):
            url = url.strip()
            if url:
                await self._input_queue.put(url)

        try:
            if isinstance(urls, t.AsyncIterable):
                async for u in urls:
                    await _put(u)
            else:
                for u in urls:
                    await _put(u)
            await self._input_queue.join()
        finally:
            await self._output_queue.put(None)

    async def resolve(self, urls: t.Union[t.AsyncIterable, t.Iterable]) -> t.AsyncGenerator[Result, None]:
        log.debug("Process urls")
        asyncio.create_task(self.put_urls(urls))
        workers = [asyncio.create_task(self.worker()) for _ in range(self._max_workers)]
        while True:
            res = await self._output_queue.get()
            if res is None:
                break
            yield res

        for task in workers:
            task.cancel()
        await asyncio.gather(*workers)
        log.debug("Urls processed")
