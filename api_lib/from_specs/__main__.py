import json
from pathlib import Path
from typing import Optional

import click

from . import lib
from .objects.components import ObjectType
from .objects.specs import Specs


def write_content_to_file(file: Path, content: Optional[str] = None):
    """Writes the content to a file."""
    if not content:
        content = ""

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
@click.option("--prefix", required=False, default=None, help="API path prefix")
def main(specs: Path, name: Path, prefix: Optional[str]):
    with specs.open("r") as file:
        specifications: Specs = Specs(json.load(file))

    # create the directory if it does not exist
    resp_folder, req_folder = lib.manage_directories(
        name / ObjectType.RESPONSE.folder, name / ObjectType.REQUEST.folder
    )

    # Create request and response files in their respectives folders
    # write_content_to_file(resp_folder / "__init__.py")
    # write_content_to_file(req_folder / "__init__.py")

    imports_strings = {type: [] for type in ObjectType}

    for cls_name, value in specifications.components.schemas.items():
        type: ObjectType = ObjectType.RESPONSE if cls_name in specifications.response_objects else ObjectType.REQUEST
        folder: Path = resp_folder if type == ObjectType.RESPONSE else req_folder

        cls_name = cls_name.split("Response")[0]
        cls_name = cls_name.split("Request")[0]

        write_content_to_file(
            folder / f"{lib.snakecase(cls_name)}.py",
            value.object_file_content(cls_name, type),
        )
        imports_strings[type].append(f"from .{lib.snakecase(cls_name)} import {cls_name} as {cls_name}")

    write_content_to_file(resp_folder / "__init__.py", "\n".join(imports_strings[ObjectType.RESPONSE]))
    write_content_to_file(req_folder / "__init__.py", "\n".join(imports_strings[ObjectType.REQUEST]))

    # Create the api.py file
    main_file_content = f"""
from typing import Optional

from api_lib import ApiLib
from api_lib.method import Method

from . import requests, responses


class {specifications.info.class_title}(ApiLib):
{'\n'.join([f"\t{line}" for line in specifications.method_strings(prefix)])}
""".strip()

    write_content_to_file(name / "api.py", main_file_content)
    write_content_to_file(name / "__init__.py")


if __name__ == "__main__":
    main()
