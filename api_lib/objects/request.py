from dataclasses import field, fields
from typing import Any, Optional

"""Defines the RequestData base class and APIfield utility for API request serialization."""


def APIfield(api_key: Optional[str] = None, default: Optional[Any] = None, **kwargs):
    """Create a dataclass field with optional API key metadata for serialization.

    Args:
        api_key: Custom key to use in API serialization.
        default: Default value for the field.
        **kwargs: Additional keyword arguments for dataclasses.field.

    Returns:
        dataclasses.Field: Configured dataclass field.
    """
    metadata = kwargs.pop("metadata", {})
    if api_key is not None:
        metadata["api_key"] = api_key

    if default is None:
        return field(metadata=metadata, **kwargs)
    else:
        return field(default=default, metadata=metadata, **kwargs)


class RequestData:
    """Base class for API request data objects, providing serialization helpers."""

    @property
    def as_dict(self) -> dict:
        """Serialize the dataclass fields to a dictionary using API keys.

        Returns:
            dict: Dictionary of API keys and their values.
        """
        result = {}
        for f in fields(self):
            api_key = f.metadata.get("api_key", f.name)
            result[api_key] = getattr(self, f.name)
        return result

    @property
    def as_header_string(self) -> str:
        """Serialize the fields as a lowercase header string.

        Returns:
            str: Header string representation.
        """
        return "&".join([f"{k}={str(v).lower()}" for k, v in self.as_dict.items()])

    @property
    def as_query_parameters(self) -> str:
        """Serialize the fields as a query parameter string, omitting None values.

        Returns:
            str: Query parameter string.
        """
        return "?" + "&".join([f"{k}={v}" for k, v in self.as_dict.items() if v is not None])

    @property
    def as_array(self) -> list:
        """Serialize the fields as a list of API keys for non-None values.

        Returns:
            list: List of API keys for non-None values.
        """
        return [f.metadata.get("api_key", f.name) for f in fields(self) if getattr(self, f.name)]
