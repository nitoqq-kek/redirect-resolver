import asyncio
import logging
import typing as t

import aiohttp
import pydantic

log = logging.getLogger(__name__)


class Result(pydantic.BaseModel):
    url: str
    real_url: t.Optional[str]
    content_length: t.Optional[int]
    http_status: t.Optional[int]
    error: t.Optional[str]


class UrlResolver:
    def __init__(self, max_workers=100):
        self._max_workers = max_workers
        self._input_queue = asyncio.Queue(maxsize=max_workers * 100)
        self._output_queue = asyncio.Queue(maxsize=max_workers * 100)

    @staticmethod
    async def resolve_url(url):
        log.debug("Processing URL: %s", url)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            try:
                async with session.get(url, max_redirects=10) as resp:
                    # yield results for each unique url in history
                    for u in {url, *(str(r.url) for r in resp.history)}:
                        yield Result(
                            url=u,
                            real_url=str(resp.real_url),
                            content_length=resp.content_length,
                            http_status=resp.status,
                        )
            except Exception as e:
                yield Result(url=url, error=f"{e.__class__.__name__}")

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
                    async for res in self.resolve_url(url):
                        await self._output_queue.put(res)
                except Exception:
                    log.exception("Unhandled exception")
                    continue
                finally:
                    self._input_queue.task_done()
                    log.debug("Finished processing URL: %s", url)

    async def put_urls(self, urls: t.Union[t.AsyncIterable, t.Iterable]):
        async def _put(url):
            url = url.strip()
            if url:
                await self._input_queue.put(u.strip())
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
