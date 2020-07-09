from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from starlette.testclient import TestClient

from kink import di, inject
import inspect

def test_decorate_async() -> None:
    di["name"] = "Bob"

    @inject
    async def example(request, name: str = "Tom") -> Response:
        body = await request.body()
        return Response(f"Hello {name}")

    application = Starlette(routes=[
        Route("/test", example, methods=["GET"])
    ])
    test_client = TestClient(application)

    response = test_client.get("/test")

