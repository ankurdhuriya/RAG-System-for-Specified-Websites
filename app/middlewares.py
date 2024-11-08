""" Middlewares."""

import os

from starlette import status
from starlette.authentication import AuthenticationError
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Api key middleware.

    This is a FastAPI ASGI middleware class that checks if the API Key
    in the request is valid.
    See https://fastapi.tiangolo.com/tutorial/middleware/ for more details.

        * If there is no API Key provided, a json response is returned with
        message "No API Token Provided" and HTTP status 403.

        * If the API Key in the request is invalid, a json response is
        returned with message "No API Token Provided" and HTTP status 403.

        * If the API Key in the response is correct, this function gets
        the response from the path operation function and returns it as-is.

    The middleware allows for public endpoints using the attribute
    `excluded_paths`. Requests to this endpoint will not be checked for a
    valid api key.

    In production, only the health endpoint should be public.

    Example:

    ```python
    from fastapi import FastAPI
    from src.middleware import ApiKeyMiddleware
    app = FastAPI()
    app.add_middleware(
        ApiKeyMiddleware,
        excluded_paths=["health", "public"],
        header_key="x-api-token",
    )
    ```
    """

    def __init__(
        self,
        app: ASGIApp,
        header_key: str = "x-api-key",
    ) -> None:
        super().__init__(app)
        self.app = app
        self.header_key = header_key

    def _is_api_key_valid(self, request: Request) -> bool:
        """Checks if api key supplied in request header is valid.

        Args:
            connection (HTTPConnection):

        Returns:
            True if api key is valid, False otherwise.

        Raises:
            AuthenticationError if the request api key could not be validated.
        """
        supplied_api_key = request.headers.get(self.header_key)

        if supplied_api_key is None:
            raise AuthenticationError("No API Token Provided.")
        elif not supplied_api_key == os.getenv("API_KEY"):
            raise AuthenticationError("Invalid API Token.")

        return True

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Dispatch method: checks the validity of a request api key.

        Args:
            request (Request):
            call_next (RequestResponseEndpoint):

        Returns:
            Response object with either error message or processed request.
        """
        try:
            self._is_api_key_valid(request)
        except AuthenticationError as error:
            return JSONResponse(
                {"message": str(error)}, status_code=status.HTTP_403_FORBIDDEN
            )

        return await call_next(request)
