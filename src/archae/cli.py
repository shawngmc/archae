"""Main CLI for archae."""

from importlib import metadata

import rich_click as click


@click.command(
    context_settings={"help_option_names": ["-h", "--help"], "show_default": True}
)
@click.rich_config(
    help_config=click.RichHelpConfiguration(
        width=88,
        show_arguments=True,
        use_rich_markup=True,
    ),
)
@click.argument("input_", metavar="INPUT")
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    help="Reverse the input.",
)
@click.version_option(metadata.version("archae"), "-v", "--version")
def cli(input_: str, *, reverse: bool = False) -> None:
    """Repeat the input.

    Archae explodes archives.
    """
    click.echo(input_ if not reverse else input_[::-1])
