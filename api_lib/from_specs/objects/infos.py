from .parser import Parser, ParserObject


@ParserObject
class Infos(Parser):
    title: str
    description: str
    version: str

    @property
    def class_title(self) -> str:
        # convert - to _ and then convert to CamelCase
        return "".join(word.capitalize() for word in self.title.replace("-", "_").split("_"))
