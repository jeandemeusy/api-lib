from dataclasses import dataclass, field, fields
from decimal import Decimal
from typing import Any, Iterable, Optional, get_args, get_origin

"""Defines the Response base class and helpers for API response serialization and metrics."""

APIobject = dataclass(init=False)


def APIfield(path: Optional[str] = None, default: Optional[object] = None):
    """Create a dataclass field with optional path and default metadata for API responses.

    Args:
        path: Path in the response object.
        default: Default value for the field.

    Returns:
        dataclasses.Field: Configured dataclass field.
    """
    metadata: dict[str, Any] = dict()
    if path:
        metadata["path"] = path
    if default:
        metadata["default"] = default

    return field(metadata=metadata)


def APImetric(labels: Optional[list[str]] = None):
    """Create a dataclass field for metrics with optional label metadata.

    Args:
        labels: List of label names for the metric.

    Returns:
        dataclasses.Field: Configured dataclass field.
    """
    metadata: dict[str, Any] = dict()
    if labels:
        metadata["labels"] = labels

    return field(metadata=metadata)


class Response:
    """Base class for API response data objects, providing serialization helpers."""
    def post_init(self):
        """Optional post-initialization hook for subclasses."""
        pass

    @property
    def is_null(self):
        """Check if all fields in the response are None.

        Returns:
            bool: True if all fields are None, False otherwise.
        """
        return all(getattr(self, key) is None for key in [f.name for f in fields(self)])

    @property
    def as_dict(self) -> dict:
        """Serialize the dataclass fields to a dictionary.

        Returns:
            dict: Dictionary of field names and their values.
        """
        return {key: getattr(self, key) for key in [f.name for f in fields(self)]}

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)


class JsonResponse(Response):
    def __init__(self, data: dict):
        """Initialize from a dictionary, mapping keys to dataclass fields.

        Args:
            data: Dictionary with data to initialize the response.
        """
        for f in fields(self):
            origin: Optional[Any] = get_origin(f.type)
            args = get_args(f.type)
            arg = args[0] if args else f.type

            v = data
            for subkey in f.metadata.get("path", f.name).split("/"):
                v = v.get(subkey, None)
                if v is None:
                    break
            if v is None:
                if default := f.metadata.get("default", None):
                    if not isinstance(default, arg):
                        raise TypeError(
                            f"Default value for {f.name} must be of type {arg.__name__}, "
                            f"got {type(default).__name__}"
                        )
                    setattr(self, f.name, default)
                else:
                    setattr(self, f.name, None)
            else:
                if origin and issubclass(origin, Iterable) and arg:
                    setattr(self, f.name, [arg(obj) for obj in v])
                else:
                    setattr(self, f.name, arg(v))
        self.post_init()


class MetricResponse(Response):
    def __init__(self, data: str):
        """Initialize from a Prometheus metrics string.

        Args:
            data: String with Prometheus metrics data.
        """
        for f in fields(self):
            args = get_args(f.type)
            arg = args[0] if args else f.type

            values = {}
            labels = f.metadata.get("labels", [])

            for line in data.split("\n"):
                if not line.strip().startswith(f.name):
                    continue

                value = line.split(" ")[-1]

                if len(labels) == 0:
                    setattr(self, f.name, arg(value) + getattr(self, f.name, 0))
                else:
                    labels_values = {
                        pair.split("=")[0].strip('"').strip(): pair.split("=")[1].strip('"').strip()
                        for pair in line.split("{")[1].split("}")[0].split(",")
                    }
                    dict_path = [labels_values[label] for label in labels if label in labels_values]
                    current = values

                    for part in dict_path[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    if dict_path[-1] not in current:
                        current[dict_path[-1]] = Decimal("0")
                    current[dict_path[-1]] += Decimal(value)

            if len(labels) > 0:
                setattr(self, f.name, arg(values))
