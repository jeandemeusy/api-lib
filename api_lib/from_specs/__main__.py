import json
from pathlib import Path

import click

from .objects.specs import Specs


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
        content: dict = json.load(file)

    specifications = Specs(content)

    # create the directory if it does not exist
    name.mkdir(parents=True, exist_ok=True)

    for key, value in specifications.components.schemas.items():
        with (name / f"{key}.py").open("w") as file:
            file.write(value.object_file_content_request(key))


if __name__ == "__main__":
    main()
