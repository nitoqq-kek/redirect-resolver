import pytest

from redirect_resolver.logging import init_logging
from testing_server.app import app


@pytest.fixture(scope="session", autouse=True)
def _init_logging():
    init_logging()


@pytest.fixture
async def server(aiohttp_server):
    return await aiohttp_server(app)
