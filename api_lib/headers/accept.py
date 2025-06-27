from typing import Optional

from .header import Header


class Accept(Header):
    """Represents the HTTP Accept header for specifying accepted response content types."""

    key: str = "Accept"
    value: str = ""

    def __init__(self, accept_type: Optional[str] = None):
        """Initialize the Accept header with a specific content type.

        Args:
            accept_type: The MIME type to accept.
        """
        if accept_type:
            self.value = accept_type


class AcceptGithub(Accept):
    """Accept header for GitHub API JSON responses."""

    value: str = "application/vnd.github+json"


class AcceptTextHtml(Accept):
    """Accept header for HTML responses."""

    value: str = "text/html"


class AcceptJson(Accept):
    """Accept header for JSON responses."""

    value: str = "application/json"


class AcceptTextPlain(Accept):
    """Accept header for plain text responses."""

    value: str = "text/plain"


class AcceptImages(Accept):
    """Accept header for image responses."""

    value: str = "image/*"


class AcceptOctetStream(Accept):
    """Accept header for binary stream responses."""

    value: str = "application/octet-stream"


class AcceptFormUrlEncoded(Accept):
    """Accept header for form URL-encoded responses."""

    value: str = "application/x-www-form-urlencoded"


class AcceptMultipartFormData(Accept):
    """Accept header for multipart form-data responses."""

    value: str = "multipart/form-data"
