from pathlib import Path
from typing import Any


def snakecase(text: str) -> str:
    if text.islower() or not text:
        return text
    return text[0].lower() + "".join("_" + x.lower() if x.isupper() else x for x in text[1:])


def manage_directories(*directories: Path):
    """Create directories if they do not exist, or clear them if they do."""
    for directory in directories:
        if directory.exists():
            for item in directory.iterdir():
                item.unlink()
            directory.rmdir()

        directory.mkdir(parents=True, exist_ok=True)

    return directories


def exported_type(_type: Any) -> str:
    type_mapping: dict[str, str] = {
        "string": "str",
        "integer": "int",
        "boolean": "bool",
        "number": "float",
        "array": "list",
        "object": "dict",
        "None": "str",
    }

    if _type and str(_type) not in type_mapping:
        for key in type_mapping.keys():
            if str(key) not in _type:
                continue
            _type = key
            break

    if _type and "null" in _type:
        return f"Optional[{type_mapping.get(_type, 'str')}]"
    else:
        return type_mapping.get(str(_type), "") if str(_type) in type_mapping else _type
