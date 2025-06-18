from dataclasses import field, fields
from typing import Any, Optional


def api_field(api_key: Optional[str] = None, default: Optional[Any] = None, **kwargs):
    metadata = kwargs.pop("metadata", {})
    if api_key is not None:
        metadata["api_key"] = api_key

    if default is None:
        return field(metadata=metadata, **kwargs)
    else:
        return field(default=default, metadata=metadata, **kwargs)


class Request:
    @property
    def as_dict(self) -> dict:
        result = {}
        for f in fields(self):
            api_key = f.metadata.get("api_key", f.name)
            result[api_key] = getattr(self, f.name)
        return result

    @property
    def as_header_string(self) -> str:
        return "&".join([f"{k}={str(v).lower()}" for k, v in self.as_dict.items()])

    @property
    def as_array(self) -> list:
        return [f.metadata["api_key"] for f in fields(self) if getattr(self, f.name)]
