import os
from typing import Optional


class Header:
    """Base class for HTTP headers.

    This class supports value assignment and optional environment variable sourcing.

    Attributes:
        key (str): The header key/name.
        prefix (str): Optional prefix for the header value (e.g., 'Bearer').
        value (str): The header value.
    """

    key: str = ""
    prefix: str = ""
    value: str = ""

    def __init__(self, value: Optional[str] = None, env_var: Optional[str] = None):
        """Initialize the header value, optionally from an environment variable.

        Args:
            value: The header value.
            env_var: Name of the environment variable to use for the value.

        Raises:
            KeyError: If env_var is provided but not set in the environment.
        """
        if env_var:
            if env_value := os.getenv(env_var):
                value = env_value.strip()
            else:
                raise KeyError(f"Environment variable '{env_var}' is not set or empty.")

        self.value = value

    @property
    def header(self) -> dict:
        """Return the header as a dictionary suitable for HTTP requests.

        Returns:
            dict: The header as a dictionary.
        """
        if self.prefix:
            return {self.key: f"{self.prefix} {self.value}"}
        else:
            return {self.key: self.value}

    def __repr__(self) -> str:
        return str(self.header)
