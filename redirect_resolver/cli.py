import logging

import click

from .logging import init_logging
from .resolver import UrlResolver
from .utils import asyncio_command


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", is_flag=True)
def main(v):
    level = logging.INFO
    if v:
        level = logging.DEBUG
    init_logging(level)


@main.command("resolve")
@click.option("-c", "--concurrency", "concurrency", type=int, default=100)
@click.argument("input_file")
@click.argument("output_file")
@asyncio_command
async def run_resolver(input_file, output_file, concurrency):
    resolver = UrlResolver(max_workers=concurrency)
    with open(input_file, "r") as inp, open(output_file, "w") as o:
        async for res in resolver.resolve(inp):
            o.write(res.json(skip_defaults=True) + "\n")
