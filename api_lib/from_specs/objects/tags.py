from .parser import Parser, ParserObject


@ParserObject
class Tags(Parser):
    name: str
    description: str
