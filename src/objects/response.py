from dataclasses import dataclass, field, fields
from decimal import Decimal
from typing import Any, Optional

APIobject = dataclass(init=False)


def APIfield(path: Optional[str] = None, default: Optional[object] = None):
    metadata: dict[str, Any] = dict()
    if path:
        metadata["path"] = path
    if default:
        metadata["default"] = default

    return field(metadata=metadata)


class Response:
    def post_init(self):
        pass

    @property
    def is_null(self):
        return all(getattr(self, key) is None for key in [f.name for f in fields(self)])

    @property
    def as_dict(self) -> dict:
        return {key: getattr(self, key) for key in [f.name for f in fields(self)]}

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return all(
            getattr(self, key) == getattr(other, key) for key in [f.name for f in fields(self)]
        )


class JsonResponse(Response):
    def __init__(self, data: dict):
        for f in fields(self):
            v = data
            for subkey in f.metadata.get("path", f.name).split("/"):
                v = v.get(subkey, None)
                if v is None:
                    break
            if v is None:
                if default := f.metadata.get("default", None):
                    if not isinstance(default, f.type):
                        raise TypeError(
                            f"Default value for {f.name} must be of type {f.type.__name__}, "  # ty: ignore[possibly-unbound-attribute]
                            f"got {type(default).__name__}"
                        )
                    setattr(self, f.name, default)
                else:
                    setattr(self, f.name, None)
            else:
                setattr(self, f.name, f.type(v))  # ty: ignore[call-non-callable]
        self.post_init()


class MetricResponse(Response):
    def __init__(self, data: str):
        for f in fields(self):
            values = {}
            labels = f.metadata.get("labels", [])

            for line in data.split("\n"):
                if not line.strip().startswith(f.name):
                    continue
                
                value = line.split(" ")[-1]

                if len(labels) == 0:
                    setattr(self, f.name, f.type(value) + getattr(self, f.name, 0))  # ty: ignore[call-non-callable]
                else:
                    labels_values = {
                        pair.split("=")[0].strip('"'): pair.split("=")[1].strip('"')
                        for pair in line.split("{")[1].split("}")[0].split(",")
                    }

                    dict_path = [labels_values[label] for label in labels]
                    current = values

                    for part in dict_path[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    if dict_path[-1] not in current:
                        current[dict_path[-1]] = Decimal("0")
                    current[dict_path[-1]] += Decimal(value)

            if len(labels) > 0:
                setattr(self, f.name, f.type(values))  # ty: ignore[call-non-callable]
