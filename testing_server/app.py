from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/self-redirect")
async def self_redirect(request):
    raise web.HTTPFound("/self-redirect")


@routes.get("/cyclic-redirect1")
async def cyclic_redirect1(request):
    raise web.HTTPFound("/cyclic-redirect2")


@routes.get("/cyclic-redirect2")
async def cyclic_redirect2(request):
    raise web.HTTPFound("/cyclic-redirect1")


@routes.get("/infinite-content")
async def infinite_content(request):
    response = web.StreamResponse()
    response.content_type = "text/plain"
    await response.prepare(request)

    try:
        while True:
            await response.write(b"aasdadasdasdasdasd")
    finally:
        await response.write_eof()
        return response


@routes.get("/large-content")
async def large_content(request):
    size = 1024 * 1024 * 1024

    response = web.StreamResponse()
    response.content_type = "text/plain"
    response.content_length = size

    await response.prepare(request)

    try:
        for i in range(size):
            await response.write(b"a")
    finally:
        await response.write_eof()
    return response


@routes.get("/content")
async def content(request):
    return web.Response(body=b"some content", content_type="text/plain")


@routes.get("/redirect-to-content")
async def redirect_to_content(request):
    raise web.HTTPFound("/content")


app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=5000)
