"""Main CLI for archae."""

from __future__ import annotations

import logging
from importlib import metadata
from pathlib import Path

import rich_click as click

from archae.config import apply_options, convert_settings
from archae.extractor import ArchiveExtractor
from archae.util.tool_manager import locate_tools

logger = logging.getLogger(__name__)


@click.command(
    context_settings={"help_option_names": ["-h", "--help"], "show_default": True}
)
@click.rich_config(
    help_config=click.RichHelpConfiguration(
        width=88,
        show_arguments=True,
        text_markup=True,
    ),
)
@click.argument(
    "archive_path",
    type=click.Path(exists=True, dir_okay=False),
    help="Archive to examine",
)
@click.option(
    "-o",
    "--opt",
    "options",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
    help="Set config options as key value pairs. Use --listopts to see available options.",
)
@click.version_option(metadata.version("archae"), "-v", "--version")
def cli(
    archive_path: str,
    options: list[tuple[str, str]] | None,
) -> None:
    """Archae explodes archives."""
    # Apply any options from the command line, then convert any convertible settings
    if options:
        apply_options(options)
    convert_settings()

    # Locate external tools
    locate_tools()

    extractor = ArchiveExtractor()
    extractor.handle_file(Path(archive_path))
    print_tracked_files(extractor.get_tracked_files())
    print_warnings(extractor.get_warnings())


def print_tracked_files(tracked_files: dict[str, dict]) -> None:
    """Print the tracked files for debugging purposes."""
    logger.info("------------------------------------------------")
    for hash, info in tracked_files.items():
        logger.info("Hash: %s", hash)
        logger.info("  Size: %s bytes", info.get("size", "Unknown"))
        for path in info.get("paths", []):
            logger.info("  Path: %s", path)
        logger.info("  Metadata:")
        for key, value in info.get("metadata", {}).items():
            logger.info("    %s: %s", key, value)


def print_warnings(warnings: list[str]) -> None:
    """Print accumulated warnings for debugging purposes."""
    logger.info("------------------------------------------------")
    logger.info("Accumulated Warnings:")
    for warning in warnings:  # type: ignore[attr-defined]
        logger.info(warning)
