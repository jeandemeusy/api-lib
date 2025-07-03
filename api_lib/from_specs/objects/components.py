from enum import Enum

from ..lib import snakecase
from .parser import Parser, ParserObject


class ObjectType(Enum):
    RESPONSE = "response"
    REQUEST = "request"

    @property
    def folder(self) -> str:
        return f"{self.value}s"


@ParserObject
class QueryObjectProperty(Parser):
    type: str
    example: str
    format: str
    example: str

    @property
    def exported_type(self) -> str:
        type_mapping: dict[str, str] = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "number": "float",
            "array": "list",
            None: "str",
        }
        _type = self.type

        if _type not in type_mapping:
            for key in type_mapping.keys():
                if key not in _type:
                    continue
                _type = key
                break

        if _type and "null" in _type:
            return f"Optional[{type_mapping.get(_type, 'str')}]"
        else:
            return type_mapping.get(_type, "str")


@ParserObject
class QueryObjects(Parser):
    type: str
    description: str
    required: list[str]
    properties: dict[str, QueryObjectProperty]

    def object_file_content(self, name: str, type: ObjectType) -> str:
        if type == ObjectType.RESPONSE:
            return self._object_file_content_response(name)
        elif type == ObjectType.REQUEST:
            return self._object_file_content_request(name)
        else:
            raise ValueError(f"Unknown object type: {type}")

    def _object_file_content_response(self, name: str) -> str:
        props = self.properties if self.properties else {}
        body: list[str] = [f"\t{key}: {value.exported_type} = APIfield()" for key, value in props.items()]
        headers = ["from api_lib.objects.response import APIfield, APIobject, JsonResponse"]

        return self._object_file_content(name, headers, body, ["@APIobject"], ["JsonResponse"])

    def _object_file_content_request(self, name: str) -> str:
        props = self.properties if self.properties else {}
        body: list[str] = []
        for key, value in props.items():
            snake_case = snakecase(key)
            custom_path = f'"{key}"' if snake_case != key else ""

            body.append(f"\t{snake_case}: {value.exported_type} = APIfield({custom_path})")

        headers = ["from dataclasses import dataclass", "from api_lib.objects.request import APIfield, RequestData"]
        return self._object_file_content(name, headers, body, ["@dataclass"], ["RequestData"])

    def _object_file_content(
        self, name: str, headers: list[str], body: list[str], decorators: list[str], parent_class: list[str]
    ) -> str:
        return f"""
{'\n'.join(headers)}

{'\n'.join(decorators)}
class {name}({', '.join(parent_class)}):
\t\"\"\"{self.description.replace("\n", " ")}\"\"\"

{'\n'.join(body)}
       """.strip()


@ParserObject
class Components(Parser):
    schemas: dict[str, QueryObjects]
    securitySchemes: dict[str, dict]
    securitySchemes: dict[str, dict]
    securitySchemes: dict[str, dict]
