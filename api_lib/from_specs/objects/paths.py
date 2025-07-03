from .parser import Parser, ParserObject


@ParserObject
class Responses(Parser):
    description: str
    content: dict[str, dict]


@ParserObject
class Query(Parser):
    tags: list[str]
    summary: str
    description: str
    operationId: str
    responses: dict[str, Responses]


@ParserObject
class Methods(Parser):
    get: Query
    post: Query
