from typing import Optional

from .components import Components
from .infos import Infos
from .parser import Parser, ParserObject
from .paths import Methods
from .tags import Tags


@ParserObject
class Specs(Parser):
    openapi: str
    info: Infos
    paths: dict[str, Methods]
    components: Components
    tags: list[Tags]

    def method_strings(self, prefix: Optional[str]) -> list[str]:
        """Returns a set of all method strings used in the paths."""
        method_strings: list[str] = list()

        for path, methods in self.paths.items():
            method_strings.extend(methods.to_methods_strings(path, prefix))

        return method_strings

    @property
    def response_objects(self) -> set[str]:
        objects: set[str] = set()

        for key, value in self.paths.items():
            for method in vars(value):
                query = getattr(value, method)

                if query is None:
                    continue

                for response in query.responses.values():
                    if response.content is None:
                        continue

                    path = ["application/json", "schema"]
                    final_path = "$ref"

                    ref = response.content
                    for part in path:
                        ref = ref.get(part, None) if ref else None

                    if ref is None:
                        continue

                    if items_ref := ref.get("items"):
                        ref = items_ref.get(final_path)
                    else:
                        ref = ref.get(final_path)

                    if ref is None:
                        continue

                    objects.add(ref.split("/")[-1])

        return objects
