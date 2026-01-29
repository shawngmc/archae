"""Main CLI for archae."""

import hashlib
from importlib import metadata
from pathlib import Path

import magic
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
@click.argument("archive_path", type=click.Path(exists=True, dir_okay=False))
@click.version_option(metadata.version("archae"), "-v", "--version")
def cli(archive_path: str) -> None:
    """Repeat the input.

    Archae explodes archives.
    """
    start_examination(archive_path)


tracked_files: dict[str, dict] = {}


def start_examination(archive_path: str) -> None:
    """Start the examination of an archive.

    Args:
        archive_path (str): The path to the archive.
    """
    click.echo(f"Starting examination of archive: {archive_path}")
    base_hash = sha256_hash_file(archive_path)
    track_file(base_hash)
    track_file_path(base_hash, archive_path)
    track_file_type(base_hash, magic.from_file(archive_path))
    debug_print_tracked_files()


def sha256_hash_file(raw_path: str) -> str:
    """Computes the SHA-256 hash of a file.

    Args:
        raw_path (str): The path to the file.

    Returns:
        str: The SHA-256 hash of the file in hexadecimal format.
    """
    try:
        file_path = Path(raw_path)
        with file_path.open("rb") as f:
            # Use hashlib.file_digest for simplicity and efficiency in Python 3.11+
            digest = hashlib.file_digest(f, "sha256")
        return digest.hexdigest()
    except FileNotFoundError:
        return "Error: File not found"


def debug_print_tracked_files() -> None:
    """Print the tracked files for debugging purposes."""
    for hash, info in tracked_files.items():
        click.echo(f"Hash: {hash}")
        for path in info.get("paths", []):
            click.echo(f"  Path: {path}")
        click.echo(f"  Type: {info.get('type', 'Unknown')}")


def track_file(hash: str) -> None:
    """Track a file by its hash.

    Args:
        hash (str): The hash of the file to track.
    """
    if hash not in tracked_files:
        tracked_files[hash] = {}


def is_file_tracked(hash: str) -> bool:
    """Check if a file is tracked by its hash.

    Args:
        hash (str): The hash of the file to check.
    """
    return hash in tracked_files


def track_file_path(hash: str, path: str) -> None:
    """Track a file path by its hash.

    Args:
        hash (str): The hash of the file.
        path (str): The path to track.
    """
    if "paths" not in tracked_files[hash]:
        tracked_files[hash]["paths"] = []

    if path not in tracked_files[hash]["paths"]:
        tracked_files[hash]["paths"].append(path)


def track_file_type(hash: str, type: str) -> None:
    """Add a type to a tracked file.

    Args:
        hash (str): The hash of the file.
        type (str): The type of the file.
    """
    tracked_files[hash]["type"] = type
