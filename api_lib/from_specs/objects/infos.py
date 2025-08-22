from .parser import Parser, ParserObject


@ParserObject
class InfosContact(Parser):
    name: str
    email: str


@ParserObject
class InfosLicense(Parser):
    name: str
    identifier: str


@ParserObject
class Infos(Parser):
    title: str
    description: str
    contact: InfosContact
    license: InfosLicense
    version: str

    @property
    def class_title(self) -> str:
        # convert - to _ and then convert to CamelCase
        return "".join(word.capitalize() for word in self.title.replace("-", "_").split("_"))
