"""HTTP method enumeration for API requests."""

from enum import Enum


class Method(Enum):
    """Enumeration of HTTP methods supported by the API client.

    Attributes:
        GET: HTTP GET method.
        POST: HTTP POST method.
        DELETE: HTTP DELETE method.
        PUT: HTTP PUT method.
        PATCH: HTTP PATCH method.
    """

    GET = "get"
    POST = "post"
    DELETE = "delete"
    PUT = "put"
    PATCH = "patch"
