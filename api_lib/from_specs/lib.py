def to_snakecase(text: str) -> str:
    if text.islower() or not text:
        return text
    return text[0].lower() + "".join("_" + x.lower() if x.isupper() else x for x in text[1:])
