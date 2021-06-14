from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from starlette.testclient import TestClient

from kink import di, inject


def test_resolve_kwargs_in_async_function() -> None:
    di["name"] = "Bob"

    @inject()
    async def example_async(request, name: str = "Tom") -> Response:
        body = await request.body()
        return Response(f"Hello {name}")

    application = Starlette(routes=[Route("/test", example_async, methods=["GET"])])
    test_client = TestClient(application)

    response = test_client.get("/test")

    assert response.status_code == 200
    assert response.content == b"Hello Bob"


def test_resolve_no_parameters_in_async() -> None:
    @inject
    async def example_async(request) -> Response:
        return Response(f"Hello Bob")

    application = Starlette(routes=[Route("/test", example_async, methods=["GET"])])
    test_client = TestClient(application)

    response = test_client.get("/test")

    assert response.status_code == 200
    assert response.content == b"Hello Bob"
