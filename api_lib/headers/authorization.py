from .header import Header


class Authorization(Header):
    """Represents the HTTP Authorization header for API authentication."""

    key: str = "Authorization"


class Bearer(Authorization):
    """Authorization header for Bearer token authentication."""

    prefix: str = "Bearer"


class Basic(Authorization):
    """Authorization header for Basic authentication."""

    prefix: str = "Basic"


class ApiKey(Authorization):
    """Authorization header for API key authentication."""

    prefix: str = "Apikey"
