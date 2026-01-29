"""Main CLI for archae."""

import contextlib
import hashlib
import shutil
import subprocess
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
    handle_file(Path(archive_path))
    debug_print_tracked_files()


tracked_files: dict[str, dict] = {}
base_dir = Path.cwd()
extract_dir = base_dir / "extracted"
if extract_dir.exists() and extract_dir.is_dir():
    shutil.rmtree(extract_dir)
extract_dir.mkdir(exist_ok=True)


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
    file_type = magic.from_file(file_path)
    track_file_type(base_hash, file_type)
    if "archive" in file_type:
        extraction_dir = extract_archive(file_path, base_hash)
        child_files = list_child_files(extraction_dir)
        for child_file in child_files:
            handle_file(child_file)


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


def extract_archive(archive_path: Path, hash: str) -> Path:
    """Extracts an archive to a specified directory.

    Args:
        archive_path (Path): The path to the archive file.
        hash (str): The hash of the archive file.

    Returns:
        Path: The path to the extracted contents.
    """
    extracted_path = extract_dir / hash
    seven_zip_path = shutil.which("7z")
    if seven_zip_path is None:
        msg = "7z command not found. Please install p7zip-full."
        raise RuntimeError(msg)
    with contextlib.suppress(FileNotFoundError):
        command = [seven_zip_path, "x", str(archive_path), "-o" + str(extracted_path)]
        subprocess.run(command, check=True)  # noqa: S603

    return extracted_path


def sha256_hash_file(file_path: Path) -> str:
    """Computes the SHA-256 hash of a file.

    Args:
        file_path (Path): The path to the file.

    Returns:
        str: The SHA-256 hash of the file in hexadecimal format.
    """
    try:
        with file_path.open("rb") as f:
            # Use hashlib.file_digest for simplicity and efficiency in Python 3.11+
            digest = hashlib.file_digest(f, "sha256")
        return digest.hexdigest()
    except FileNotFoundError:
        return "Error: File not found"


def debug_print_tracked_files() -> None:
    """Print the tracked files for debugging purposes."""
    click.echo("------------------------------------------------")
    for hash, info in tracked_files.items():
        click.echo(f"Hash: {hash}")
        for path in info.get("paths", []):
            click.echo(f"  Path: {path}")
        click.echo(f"  Type: {info.get('type', 'Unknown')}")
        click.echo(f"  Size: {info.get('size', 'Unknown')} bytes")


def track_file(hash: str, file_size_bytes: int) -> None:
    """Track a file by its hash.

    Args:
        hash (str): The hash of the file to track.
        file_size_bytes (int): The size of the file in bytes.
    """
    if hash not in tracked_files:
        tracked_files[hash] = {}
        tracked_files[hash]["size"] = file_size_bytes
    elif tracked_files[hash]["size"] != file_size_bytes:
        msg = f"Hash collision detected for hash {hash} with differing sizes."
        raise RuntimeError(msg)


def is_file_tracked(hash: str) -> bool:
    """Check if a file is tracked by its hash.

    Args:
        hash (str): The hash of the file to check.
    """
    return hash in tracked_files


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


def track_file_type(hash: str, type: str) -> None:
    """Add a type to a tracked file.

    Args:
        hash (str): The hash of the file.
        type (str): The type of the file.
    """
    tracked_files[hash]["type"] = type
