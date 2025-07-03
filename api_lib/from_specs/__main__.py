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

    for cls_name, value in specifications.components.schemas.items():
        type: ObjectType = ObjectType.RESPONSE if cls_name in specifications.response_objects else ObjectType.REQUEST
        folder: Path = resp_folder if type == ObjectType.RESPONSE else req_folder

        write_content_to_file(
            folder / f"{lib.snakecase(cls_name)}.py",
            value.object_file_content(cls_name, type),
        )


if __name__ == "__main__":
    main()
