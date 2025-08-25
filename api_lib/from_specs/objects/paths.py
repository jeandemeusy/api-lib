from typing import Optional

from ..lib import exported_type, snakecase, split_line_into_multiple_lines
from .parser import Parser, ParserObject


@ParserObject
class Responses(Parser):
    description: str
    content: dict

    @property
    def schema(self) -> str:
        """Returns the schema reference if available."""
        is_array = False
        ret_type = None
        if not self.content:
            return "bool"

        if self.content.get("application/json", None):
            ret_type = "application/json"
        elif self.content.get("text/plain", None):
            ret_type = "text/plain"
        else:
            return "NO_APPLICATION_JSON"

        if not self.content[ret_type].get("schema", None):
            return "NO_SCHEMA"

        if self.content[ret_type]["schema"].get("type", None) == "array":
            is_array = True
            ref = self.content[ret_type]["schema"]["items"]["$ref"]
        elif self.content[ret_type]["schema"].get("$ref", None):
            ref = self.content[ret_type]["schema"]["$ref"]
        elif self.content[ret_type]["schema"].get("type", None):
            ref = self.content[ret_type]["schema"]["type"]
        else:
            ref = "NO_REF"

        ref: str = ref.split("/")[-1].split("Response")[0] if ref else "NO_REF"

        if ref not in ["string", "integer", "boolean"]:
            ref = f"responses.{ref}"

        if is_array:
            return f"list[{ref}]"
        else:
            return ref


@ParserObject
class Query(Parser):
    tags: list[str]
    summary: str
    description: str
    operationId: str
    responses: dict[str, Responses]

    @property
    def method_name(self) -> str:
        """Returns the method name in a string format."""
        return self.operationId.replace("-", "_").replace(" ", "_").lower()

    @property
    def multiline_description(self) -> list[str]:
        lines: list[str] = split_line_into_multiple_lines(self.description.replace("\n", " "), 92)

        return [f"\t{line}" for line in lines]


    def to_method_string(self, path: str, method: str, prefix: Optional[str]) -> list[str]:
        """Returns the method name in a string format."""
        response = next((resp for code, resp in self.responses.items() if str(code).startswith("2")), None)

        ret_type = exported_type(response.schema) if response else "None"

        use_api_prefix = prefix and path.startswith(prefix)
        full_path = path.split(prefix, 1)[1] if use_api_prefix else path
        sub_paths = full_path.split("/")

        params = ["self"]
        formatted_path = []
        for sub_path in sub_paths:
            if sub_path.startswith("{") and sub_path.endswith("}"):
                params.append(snakecase(f"{sub_path[1:-1]}: str"))
                formatted_path.append(snakecase(f"{'{'}{sub_path[1:-1]}{'}'}"))
            else:
                formatted_path.append(sub_path)

        path = "/".join(formatted_path)

        # definition line
        def_line: str = f"def {self.method_name}({', '.join(params)}) -> Optional[{ret_type}]:"
        
        # comment line
        description_lines = []
        if self.description:
            description_lines = ['\t"""'] + self.multiline_description + ['\t"""']

        # return line
        params: list[str] = [f"Method.{method.upper()}", f'{'f' if len(params) > 1 else ''}"{path}"', ret_type]

        if not use_api_prefix:
            params += ["use_api_prefix=False"]
            if ret_type == "bool":
                params += ["return_state=True"]

        return_line: str = f"return self.try_req({', '.join(params)})"
        return [def_line, *description_lines, f"\t{return_line}\n"]


@ParserObject
class Methods(Parser):
    get: Query
    post: Query
    delete: Query
    put: Query
    patch: Query

    def to_methods_strings(self, path: str, prefix: Optional[str]) -> list[str]:
        """Returns a list of method names in string format."""
        methods = []
        for method in vars(self):
            query: Query = getattr(self, method)
            if query is not None:
                methods.extend(query.to_method_string(path, method, prefix))

        return methods
