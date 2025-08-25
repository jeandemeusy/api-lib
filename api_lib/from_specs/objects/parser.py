from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Optional, get_args, get_origin

ParserObject = dataclass(init=False)


class Parser:
    def __init__(self, data: Optional[dict] = None):
        if data is None:
            data = {}

        for f in fields(self):
            field_type = f.type
            field_name = f.name

            origin: Optional[Any] = get_origin(field_type)
            args = get_args(field_type)
            value = data.get(field_name, None)

            if value is None:
                setattr(self, field_name, None)
                continue

            if is_dataclass(field_type):
                value = field_type(value)
            elif origin is list and len(args) == 1 and is_dataclass(args[0]):
                value = [args[0](item) if not isinstance(item, args[0]) else item for item in value]
            elif origin is dict and len(args) == 2 and args[0] is str and is_dataclass(args[1]):
                value = {k: args[1](v) if not isinstance(v, args[1]) else v for k, v in value.items()}
            else:
                args = (*args, field_type)
                value = args[0](value)

            setattr(self, f.name, value)

    def __repr__(self):
        key_pair_string: str = ", ".join([f"{key}={value}" for key, value in vars(self).items()])
        return f"{self.__class__.__name__}({key_pair_string})"
