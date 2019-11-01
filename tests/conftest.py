import pytest
from aiohttp import web

from redirect_resolver.logging import init_logging
from testing_server.app import routes


@pytest.fixture(scope="session", autouse=True)
def _init_logging():
    init_logging()


@pytest.fixture
def app(loop):
    app = web.Application(loop=loop)
    app.add_routes(routes)
    return app


@pytest.fixture
async def server(aiohttp_server, app):
    return await aiohttp_server(app)
