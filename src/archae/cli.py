"""Main CLI for archae."""

from __future__ import annotations

import copy
import hashlib
import shutil
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any

import magic
import rich_click as click

import archae.util.archiver
from archae.config import apply_options, convert_settings, settings

if TYPE_CHECKING:
    from archae.util.archiver.base_archiver import BaseArchiver

tools: dict[str, BaseArchiver] = {}


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
    options: tuple[list[tuple[str, str]]],
) -> None:
    """Archae explodes archives."""
    # Apply any options from the command line, then convert any convertible settings
    if options:
        apply_options(options)
    convert_settings()

    # Locate external tools
    locate_tools()

    handle_file(Path(archive_path))
    debug_print_tracked_files()


tracked_files: dict[str, dict] = {}
base_dir = Path.cwd()
extract_dir = base_dir / "extracted"
if extract_dir.exists() and extract_dir.is_dir():
    shutil.rmtree(extract_dir)
extract_dir.mkdir(exist_ok=True)


def locate_tools() -> None:
    """Locate external tools."""
    for cls in archae.util.archiver.BaseArchiver.__subclasses__():
        tool_path = shutil.which(str(cls.executable_name))
        if tool_path is not None:
            tools[str(cls.archiver_name)] = cls(tool_path)  # type: ignore[abstract]


def handle_file(file_path: Path) -> None:
    """Handle a file given its path.

    Args:
        file_path (Path): The path to the file.
    """
    click.echo(f"Starting examination of file: {file_path!s}")

    base_hash = sha256_hash_file(file_path)
    file_size_bytes = file_path.stat().st_size
    track_file(base_hash, file_size_bytes)
    track_file_path(base_hash, file_path)
    add_metadata_to_hash(base_hash, "type", magic.from_file(file_path))
    add_metadata_to_hash(base_hash, "type_mime", magic.from_file(file_path, mime=True))
    extension = file_path.suffix.lstrip(".").lower()
    add_metadata_to_hash(base_hash, "extension", extension)
    is_file_archive = is_archive(base_hash)
    add_metadata_to_hash(base_hash, "is_archive", is_file_archive)
    if is_file_archive:
        archiver = get_archiver_for_file(base_hash)
        if archiver:
            extracted_size = archiver.get_archive_uncompressed_size(file_path)
            add_metadata_to_hash(base_hash, "extracted_size", extracted_size)
            compression_ratio = extracted_size / file_size_bytes
            add_metadata_to_hash(
                base_hash, "overall_compression_ratio", compression_ratio
            )
            if extracted_size > settings["MAX_ARCHIVE_SIZE_BYTES"]:
                click.echo(
                    f"Skipped archive {file_path} because expected size {extracted_size} is greater than MAX_ARCHIVE_SIZE_BYTES {settings['MAX_ARCHIVE_SIZE_BYTES']}"
                )
            elif (
                get_tracked_file_size() + extracted_size
                > settings["MAX_TOTAL_SIZE_BYTES"]
            ):
                click.echo(
                    f"Skipped archive {file_path} because expected size {extracted_size} + current tracked files {get_tracked_file_size()} is greater than MAX_TOTAL_SIZE_BYTES {settings['MAX_TOTAL_SIZE_BYTES']}"
                )
            elif compression_ratio < settings["MIN_ARCHIVE_RATIO"]:
                click.echo(
                    f"Skipped archive {file_path} because compression ratio {compression_ratio:.5f} is less than MIN_ARCHIVE_RATIO {settings['MIN_ARCHIVE_RATIO']}"
                )
            elif (
                shutil.disk_usage(base_dir).free - extracted_size
                > settings["MIN_DISK_FREE_SPACE"]
            ):
                click.echo(
                    f"Skipped archive {file_path} because extracting it would leave less than MIN_DISK_FREE_SPACE {settings['MIN_DISK_FREE_SPACE']} bytes free at extraction location {base_dir!s}"
                )
            else:
                extraction_dir = extract_dir / base_hash
                archiver.extract_archive(file_path, extraction_dir)
                child_files = list_child_files(extraction_dir)
                for child_file in child_files:
                    handle_file(child_file)
        else:
            click.echo(f"No suitable archiver found for file: {file_path!s}")


def is_archive(hash: str) -> bool:
    """Determine the appropriate archiver for a file based on its metadata.

    Args:
        hash (str): The hash of the file.

    Returns:
        bool: True if the file is an archive, otherwise False.

    """
    metadata = get_tracked_file_metadata(hash)
    mime_type = metadata.get("type_mime", "").lower()
    extension = metadata.get("extension", "").lower()

    for tool in tools.values():
        if mime_type in tool.mime_types or extension in tool.file_extensions:
            return True

    return False


def get_archiver_for_file(hash: str) -> BaseArchiver | None:
    """Determine the appropriate archiver for a file based on its metadata.

    Args:
        hash (str): The hash of the file.

    Returns:
        str | None: The name of the archiver tool if found, otherwise None.
    """
    metadata = get_tracked_file_metadata(hash)
    mime_type = metadata.get("type_mime", "").lower()
    extension = metadata.get("extension", "").lower()

    for tool in tools.values():
        if mime_type in tool.mime_types or extension in tool.file_extensions:
            return tool
    return None


def list_child_files(directory_path: Path, pattern: str = "*") -> list[Path]:
    """Recursively get a list of files matching a pattern in a directory.

    Args:
        directory_path (Path): The starting directory path.
        pattern (str): The file pattern to match (e.g., '*.txt', '*.py').

    Returns:
        list: A list of Path objects for the matching files.
    """
    # rglob performs a recursive search
    files = list(directory_path.rglob(pattern))
    # Optionally, filter out directories if pattern='*'
    return [file for file in files if file.is_file()]


def sha256_hash_file(file_path: Path) -> str:
    """Computes the SHA-256 hash of a file.

    Args:
        file_path (Path): The path to the file.

    Returns:
        str: The SHA-256 hash of the file in hexadecimal format.
    """
    try:
        with file_path.open("rb") as f:
            digest = hashlib.file_digest(f, "sha256")
        return digest.hexdigest()
    except FileNotFoundError:
        return "Error: File not found"


def debug_print_tracked_files() -> None:
    """Print the tracked files for debugging purposes."""
    click.echo("------------------------------------------------")
    for hash, info in tracked_files.items():
        click.echo(f"Hash: {hash}")
        click.echo(f"  Size: {info.get('size', 'Unknown')} bytes")
        for path in info.get("paths", []):
            click.echo(f"  Path: {path}")
        click.echo("  Metadata:")
        for key, value in info.get("metadata", {}).items():
            click.echo(f"    {key}: {value}")


def track_file(hash: str, file_size_bytes: int) -> None:
    """Track a file by its hash.

    Args:
        hash (str): The hash of the file to track.
        file_size_bytes (int): The size of the file in bytes.
    """
    if hash not in tracked_files:
        tracked_files[hash] = {}
        tracked_files[hash]["size"] = file_size_bytes
        tracked_files[hash]["metadata"] = {}
    elif tracked_files[hash]["size"] != file_size_bytes:
        msg = f"Hash collision detected for hash {hash} with differing sizes."
        raise RuntimeError(msg)


def is_file_tracked(hash: str) -> bool:
    """Check if a file is tracked by its hash.

    Args:
        hash (str): The hash of the file to check.
    """
    return hash in tracked_files


def get_tracked_file_metadata(hash: str) -> dict:
    """Get metadata for a tracked file by its hash.

    Args:
        hash (str): The hash of the file.

    Returns:
        dict: The metadata of the tracked file.
    """
    return copy.deepcopy(tracked_files.get(hash, {}).get("metadata", {}))


def track_file_path(hash: str, file_path: Path) -> None:
    """Track a file path by its hash.

    Args:
        hash (str): The hash of the file.
        file_path (Path): The path to track.
    """
    if "paths" not in tracked_files[hash]:
        tracked_files[hash]["paths"] = []

    if file_path not in tracked_files[hash]["paths"]:
        tracked_files[hash]["paths"].append(file_path)


def add_metadata_to_hash(hash: str, key: str, value: Any) -> None:
    """Add metadata to a tracked file.

    Args:
        hash (str): The hash of the file.
        key (str): The metadata key.
        value (Any): The metadata value.
    """
    tracked_files[hash]["metadata"][key] = value


def get_tracked_file_size() -> int:
    """Get the total size of all tracked files.

    Returns:
        int: The total size in bytes.
    """
    return sum(tracked_files[hash].get("size", 0) for hash in tracked_files)
