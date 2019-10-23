import asyncio
import typing as t
from functools import wraps


def asyncio_command(f: t.Callable) -> t.Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper
