from pathlib import Path


def snakecase(text: str) -> str:
    if text.islower() or not text:
        return text
    return text[0].lower() + "".join("_" + x.lower() if x.isupper() else x for x in text[1:])


def manage_directories(*directories: Path):
    """Create directories if they do not exist, or clear them if they do."""
    for directory in directories:
        if directory.exists():
            for item in directory.iterdir():
                item.unlink()
            directory.rmdir()

        directory.mkdir(parents=True, exist_ok=True)

    return directories
