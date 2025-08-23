from enum import Enum
from typing import Optional

from ..lib import exported_type, snakecase
from .parser import Parser, ParserObject


class ObjectType(Enum):
    RESPONSE = "response"
    REQUEST = "request"

    @property
    def folder(self) -> str:
        return f"{self.value}s"


@ParserObject
class QueryObjectProperty(Parser):
    default: Optional[str]
    description: str
    example: str
    format: str
    type: str


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
        body = []
        for key, value in props.items():
            exported_key = snakecase(key)

            line = f"\t{exported_key}: {exported_type(value.type)}"
            if exported_key != key:
                line += f' = APIfield("{key}")'
            body.append(line)
        headers = ["from api_lib.objects.response import APIfield, APIobject, JsonResponse"]

        return self._object_file_content(name, headers, body, ["@APIobject"], ["JsonResponse"])

    def _object_file_content_request(self, name: str) -> str:
        props = self.properties if self.properties else {}
        body: list[str] = []
        for key, value in props.items():
            snake_case = snakecase(key)

            line = f"\t{snake_case}: {exported_type(value.type)}"

            params = []
            if snake_case != key:
                params.append(f'"{key}"')
            if value.default:
                params.append(value.default)

            if len(params) > 0:
                line += f"= APIfield({','.join(params)})"

            body.append(line)

        headers = ["from dataclasses import dataclass", "from api_lib.objects.request import APIfield, RequestData"]
        return self._object_file_content(name, headers, body, ["@dataclass"], ["RequestData"])

    def _object_file_content(
        self, name: str, headers: list[str], body: list[str], decorators: list[str], parent_class: list[str]
    ) -> str:
        description_str = self.description.replace("\n", " ")

        descriptions_lines = []
        description_words = description_str.split(" ")

        if len(description_words) == 0:
            description_str = "No description"
            descriptions_lines = [description_str]
        else:
            index = 0
            while len(description_words) > 0:
                descriptions_lines.append("")
                while (len(descriptions_lines[index]) + len(description_words[0]) + 1) <= 95:
                    descriptions_lines[index] += f" {description_words.pop(0)}"
                    if len(description_words) == 0:
                        break
                descriptions_lines[index] = descriptions_lines[index].strip()
                index += 1

        return f"""
{'\n'.join(headers)}

{'\n'.join(decorators)}
class {name}({', '.join(parent_class)}):
\t\"\"\"\n\t{'\n\t'.join(descriptions_lines)}\n\t\"\"\"

{'\n'.join(body)}
       """.strip()


@ParserObject
class Components(Parser):
    schemas: dict[str, QueryObjects]
    securitySchemes: dict[str, dict]
