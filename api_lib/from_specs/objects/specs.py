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
