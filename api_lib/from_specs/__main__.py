import json
from pathlib import Path

import click

from . import lib
from .objects.components import ObjectType
from .objects.specs import Specs


def write_content_to_file(file: Path, content: str):
    """Writes the content to a file."""
    with file.open("w") as f:
        f.write(content)


@click.command()
@click.option(
    "--specs",
    "-s",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the specifications file.",
)
@click.option(
    "--name",
    "-n",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Path where to store the generated files.",
)
def main(specs: Path, name: Path):
    with specs.open("r") as file:
        specifications: Specs = Specs(json.load(file))

    # create the directory if it does not exist
    resp_folder, req_folder = lib.manage_directories(
        name / ObjectType.RESPONSE.folder, name / ObjectType.REQUEST.folder
    )

    for cls, value in specifications.components.schemas.items():
        filename: str = lib.to_snakecase(cls)
        type: ObjectType = ObjectType.RESPONSE if cls in specifications.response_objects else ObjectType.REQUEST

        content: str = value.object_file_content(cls, type)
        write_content_to_file(resp_folder / f"{filename}.py", content)


if __name__ == "__main__":
    main()
