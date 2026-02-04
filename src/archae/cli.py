"""Main CLI for archae."""

from __future__ import annotations

import logging
import pathlib
from importlib import metadata
from pathlib import Path

import rich_click as click

from archae.config import apply_options, get_options
from archae.extractor import ArchiveExtractor
from archae.util.tool_manager import ToolManager

logger = logging.getLogger("archae")
logger.setLevel(logging.INFO)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"], "show_default": True}
)
@click.rich_config(
    help_config=click.RichHelpConfiguration(
        width=88,
        show_arguments=True,
        text_markup=True,
    ),
)
@click.version_option(metadata.version("archae"), "-v", "--version")
def cli() -> None:
    """Archae explodes archives."""


@cli.command()
@click.argument(
    "archive_path",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path),
    default=Path.cwd() / "extracted",
    help="Archive to examine",
)
@click.option(
    "-o",
    "--opt",
    "options",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
    help="Set config options as key value pairs. Use 'archae listopts' to see available options.",
)
@click.option(
    "-e",
    "--extract-dir",
    "extract_dir",
    nargs=1,
    type=click.Path(
        dir_okay=True,
        file_okay=False,
        readable=True,
        writable=True,
        path_type=pathlib.Path,
    ),
    default=Path.cwd() / "extracted",
    help="Set config options as key value pairs. Use 'archae listopts' to see available options.",
)
def extract(
    archive_path: pathlib.Path,
    options: list[tuple[str, str | int | float | bool]] | None,
    extract_dir: pathlib.Path,
) -> None:
    """Extract and analyze an archive."""
    # Apply any options from the command line, then convert any convertible settings
    if options:
        apply_options(options)

    # Locate external tools
    ToolManager.locate_tools()
    extractor = ArchiveExtractor(extract_dir=extract_dir)
    extractor.handle_file(archive_path)
    print_tracked_files(extractor.get_tracked_files())
    print_warnings(extractor.get_warnings())


@cli.command()
def listopts() -> None:
    """List all available configuration options."""
    options = get_options()

    # Load default settings
    defaults_path = Path(__file__).parent / "default_settings.toml"
    defaults_content = defaults_path.read_text()
    defaults = {}
    in_default_section = False
    for line in defaults_content.split("\n"):
        if line.strip() == "[default]":
            in_default_section = True
            continue
        if in_default_section and line.startswith("["):
            break
        if in_default_section and "=" in line:
            key, value = line.split("=", 1)
            defaults[key.strip()] = value.strip().strip('"')

    logger.info("Available configuration options:")
    logger.info("------------------------------------------------")
    for option_name, option_def in sorted(options.items()):
        logger.info("%s (%s)", option_name, option_def.get("type", "unknown"))
        logger.info("  %s", option_def.get("help", "No description available"))
        if option_name in defaults:
            logger.info("  Default: %s", defaults[option_name])


@cli.command()
def status() -> None:
    """Show archae status and available tools."""
    logger.info("Archae status:")
    logger.info("Version: %s", metadata.version("archae"))
    ToolManager.locate_tools()
    logger.info("Tools located and ready to use.")
    logger.info("------------------------------------------------")

    # Show supported extensions
    supported_ext = ToolManager.get_supported_extensions()
    logger.info("Supported file extensions (%d):", len(supported_ext))
    if supported_ext:
        logger.info("  %s", ", ".join(supported_ext))
    else:
        logger.info("  (none)")

    # Show unsupported extensions
    unsupported_ext = ToolManager.get_unsupported_extensions()
    logger.info("Unsupported file extensions (%d):", len(unsupported_ext))
    if unsupported_ext:
        logger.info("  %s", ", ".join(unsupported_ext))
    else:
        logger.info("  (none)")

    logger.info("------------------------------------------------")

    # Show supported MIME types
    supported_mime = ToolManager.get_supported_mime_types()
    logger.info("Supported MIME types (%d):", len(supported_mime))
    if supported_mime:
        logger.info("  %s", ", ".join(supported_mime))
    else:
        logger.info("  (none)")

    # Show unsupported MIME types
    unsupported_mime = ToolManager.get_unsupported_mime_types()
    logger.info("Unsupported MIME types (%d):", len(unsupported_mime))
    if unsupported_mime:
        logger.info("  %s", ", ".join(unsupported_mime))
    else:
        logger.info("  (none)")


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
    if len(warnings) == 0:
        logger.info("No warnings.")
        return
    logger.info("Accumulated Warnings:")
    for warning in warnings:  # type: ignore[attr-defined]
        logger.info(warning)
