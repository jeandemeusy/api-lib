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

        ref = ref.split("/")[-1] if ref else "NO_REF"

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
    def to_method_string(self) -> list[str]:
        response = next(
            (resp for code, resp in self.responses.items() if str(code).startswith("2")),
            None
        )
        if response:
            ret_type = response.schema
        else:
            ret_type = "None"

        """Returns the method name in a string format."""
        return [
            f"def {self.method_name}(self) -> {ret_type}:",
            "\tpass\n"
        ]


@ParserObject
class Methods(Parser):
    get: Query
    post: Query
    delete: Query
    put: Query
    patch: Query

    @property
    def to_methods_strings(self) -> list[str]:
        """Returns a list of method names in string format."""
        methods = []
        for method in vars(self):
            query = getattr(self, method)
            if query is not None:
                methods.extend(query.to_method_string)
                
        return methods
