"""Main CLI for archae."""

from __future__ import annotations

import contextlib
import hashlib
import shutil
import subprocess
from importlib import metadata
from pathlib import Path
from typing import Any
import re
import copy
from enum import Enum

import magic
import rich_click as click

tool_names = [
    "7z",
    "pea",
    "unar",
]

mime_types_7z = [
    "application/x-7z-compressed",
    "application/vnd.android.package-archive",
    "application/x-bzip2",
    "application/x-chrome-extension",
    "application/x-xpinstall",
    "application/vnd.debian.binary-package",
    "application/gzip",
    "application/java-archive",
    "application/x-lzma",
    "application/vnd.ms-cab-compressed",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msix",
    "application/appinstaller",
    "application/appx",
    "application/appxbundle",
    "application/msixbundle",
    "application/x-compress",
    "application/x-tar",
    "application/zip",
    "application/x-apple-diskimage",
    "application/x-arj",
    "application/x-cpio",
    "application/vnd.efi.img",
    "application/x-alz-compressed",
    "application/x-xar",
    "application/x-iso9660-image",
    "application/x-lzh",
    "application/vnd.ms-htmlhelp",
    "application/x-ole-storage",
    "application/x-vhd",
    "text/x-nsis",
    "application/x-qemu-disk",
    "application/x-rpm",
    "application/x-rar-compressed",
    "application/vnd.squashfs",
    "application/x-archive",
    "application/x-virtualbox-vdi",
    "application/x-vmdk-disk",
    "application/x-ms-wim",
    "application/x-xz",
]

extensions_7z = [
    "7z",
    "s7z",
    "apk",
    "bz2",
    "tbz2",
    "crx",
    "xpi",
    "deb",
    "gz",
    "tgz",
    "ipa",
    "jar",
    "ear",
    "war",
    "lzma",
    "cab",
    "docx",
    "docm",
    "pptx",
    "pptm",
    "xlsx",
    "xlsm",
    "emsix",
    "emsixbundle",
    "msix",
    "appinstaller",
    "appx",
    "appxbundle",
    "msixbundle",
    "z",
    "taz",
    "tar",
    "zip",
    "zipx",
    "appimage",
    "dmg ",
    "img",
    "arj",
    "cpio",
    "cramfs",
    "raw",
    "alz",
    "ext",
    "ext2",
    "ext3",
    "ext4",
    "xar",
    "pkg",
    "fat",
    "gpt",
    "hfs",
    "hfsx",
    "iso",
    "lha",
    "lhz",
    "mbr",
    "chm",
    "chw",
    "chi",
    "chq",
    "msi",
    "msp",
    "vhd",
    "vhdx",
    "ntfs",
    "nsi",
    "exe",
    "nsis",
    "qcow2",
    "qcow",
    "qcow2c",
    "rpm",
    "rar",
    "r00",
    "sqfs",
    "sfs",
    "sqsh",
    "squashfs",
    "scap",
    "uefif",
    "udf",
    "edb",
    "edp",
    "edr",
    "a",
    "ar",
    "deb",
    "lib",
    "vdi",
    "vmdk",
    "wim",
    "swm",
    "esd",
    "xz",
    "txz",
]

mime_types_pea = [
    "application/appinstaller",
    "application/appx",
    "application/appxbundle",
    "application/gzip",
    "application/java-archive",
    "application/msix",
    "application/msixbundle",
    "application/vnd.android.package-archive",
    "application/vnd.debian.binary-package",
    "application/vnd.ms-cab-compressed",
    "application/vnd.ms-htmlhelp",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/x-7z-compressed",
    "application/x-ace-compressed",
    "application/x-apple-diskimage",
    "application/x-arc",
    "application/x-arj",
    "application/x-brotli",
    "application/x-bzip2",
    "application/x-chrome-extension",
    "application/x-compress",
    "application/x-cpio",
    "application/x-freearc",
    "application/x-iso9660-image",
    "application/x-lzma",
    "application/x-ms-wim",
    "application/x-ole-storage",
    "application/x-rar-compressed",
    "application/x-rpm",
    "application/x-tar",
    "application/x-vhd",
    "application/x-xar",
    "application/x-xpinstall",
    "application/x-xz",
    "application/zip",
    "application/zip",
    "application/zip",
    "application/zstd",
]

extensions_pea = [
    "appinstaller",
    "appx",
    "appxbundle",
    "gz",
    "tgz",
    "jar",
    "ear",
    "war",
    "emsix",
    "emsixbundle",
    "msix",
    "msixbundle",
    "apk",
    "deb",
    "cab",
    "chm",
    "chw",
    "chi",
    "chq",
    "pptx",
    "pptm ",
    "xlsx",
    "xlsm",
    "docx",
    "docm",
    "7z",
    "s7z",
    "ace",
    "dmg",
    "img",
    "arc",
    "pak",
    "arj",
    "br",
    "bz2",
    "tbz2",
    "crx",
    "z",
    "taz",
    "cpio",
    "arc",
    "pak",
    "iso",
    "img",
    "lzma",
    "wim",
    "swm",
    "esd",
    "msi",
    "msp",
    "rar",
    "r00",
    "rpm",
    "tar",
    "vhd",
    "vhdx",
    "xar",
    "pkg",
    "xpi",
    "xz",
    "txz",
    "ipa",
    "zip",
    "zipx",
    "aar",
    "zst",
]

mime_types_unar = [
    "application/appinstaller",
    "application/appx",
    "application/appxbundle",
    "application/gzip",
    "application/msix",
    "application/msixbundle",
    "application/vnd.android.package-archive",
    "application/vnd.debian.binary-package",
    "application/vnd.ms-cab-compressed",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/x-7z-compressed",
    "application/x-ace-compressed",
    "application/x-alz-compressed",
    "application/x-arc",
    "application/x-archive",
    "application/x-arj",
    "application/x-bzip2",
    "application/x-chrome-extension",
    "application/x-compress",
    "application/x-cpio",
    "application/x-freearc",
    "application/x-iso9660-image",
    "application/x-lzh",
    "application/x-lzma",
    "application/x-ole-storage",
    "application/x-rar-compressed",
    "application/x-stuffit",
    "application/x-sit",
    "application/x-stuffitx",
    "application/x-sitx",
    "application/x-tar",
    "application/x-xar",
    "application/x-xpinstall",
    "application/x-xz",
    "application/x-zoo",
    "application/zip",
    "application/zip",
    "text/x-nsis",
]

extensions_unar = [
    "appinstaller",
    "appx",
    "appxbundle",
    "gz",
    "tgz",
    "emsix",
    "emsixbundle",
    "msix",
    "msixbundle",
    "apk",
    "deb",
    "cab",
    "pptx",
    "pptm ",
    "xlsx ",
    "xlsm",
    "docx",
    "docm",
    "7z",
    "s7z",
    "ace",
    "alz",
    "arc",
    "pak",
    "a",
    "ar",
    "deb",
    "lib",
    "arj",
    "bz2",
    "tbz2",
    "crx",
    "z",
    "taz",
    "cpio",
    "arc",
    "pak",
    "iso",
    "img",
    "lha",
    "lhz",
    "lzma",
    "msi",
    "msp",
    "rar",
    "r00",
    "sit",
    "sitx",
    "tar",
    "xar",
    "pkg",
    "xpi",
    "xz",
    "txz",
    "zoo",
    "zip",
    "zipx",
    "aar",
    "nsi",
    "exe",
    "nsis",
    "udf",
    "edb",
    "edp",
    "edr",
]

tools = {}


class ByteScale(Enum):
    NONE = (0, "")
    KILO = (1, "K")
    MEGA = (2, "M")
    GIGA = (3, "G")
    TERA = (4, "T")
    PETA = (5, "P")
    
    def __new__(cls, exponent, prefix_letter):
        """
        __new__ is used to control how new enum members are instantiated.
        It must set the `_value_` attribute and any custom attributes.
        """
        obj = object.__new__(cls)
        obj._value_ = exponent
        obj.prefix_letter = prefix_letter
        return obj

    @property
    def set_prefix_letter(self):
        obj.prefix_letter = prefix_letter

    @property
    def get_prefix_letter(self):
        return self.prefix_letter

class FileSizeParamType(click.ParamType):
    name = "filesize"

    @staticmethod
    def compact_value(value):
        exponent = 0
        modulo = 0
        while modulo == 0 and exponent < 4:
            modulo = value % 1024
            if modulo == 0:
                exponent += 1
                value = int(value / 1024)
        return f"{value}{ByteScale(exponent).get_prefix_letter}"
            
    
    @staticmethod
    def expand_value(value):
        try:
            return int(value)
        except:
            pass

        # Regex to split number and unit
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]B?)$', value, re.IGNORECASE)
        if not match:
            raise ValueError(f"{value} is not a valid file size (e.g., 10G, 500M)")
        
        number, unit = match.groups()
        number = float(number)
        unit = unit.upper()

        units = {
            'K': 1024,
            'KB': 1024,
            'M': 1024**2,
            'MB': 1024**2,
            'G': 1024**3,
            'GB': 1024**3,
            'T': 1024**4,
            'TB': 1024**4,
        }
        
        # Default to bytes if no specific unit multiplier, or assume B
        return int(number * units.get(unit, 1))

    def convert(self, value, param, ctx):
        try:
            return self.expand_value(value)
        except ValueError as err:
            self.fail(str(err), param, ctx)

defaults = {
    "max_total_size_bytes": FileSizeParamType.expand_value("100G"),
    "max_archive_size_bytes": FileSizeParamType.expand_value("10G"),
    "min-archive_ratio": 0.005
}

config = copy.deepcopy(defaults)

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
@click.argument("archive_path", type=click.Path(exists=True, dir_okay=False), help="Archive to examine")
@click.option("--max_total_size_bytes", type=FileSizeParamType(), default=defaults["max_total_size_bytes"], help=f"Maximum total extraction size before failing, default {FileSizeParamType.compact_value(defaults['max_total_size_bytes'])}")
@click.option("--max_archive_size_bytes", type=FileSizeParamType(), default=defaults["max_archive_size_bytes"], help=f"Maximum individual archive extraction size before failing, default {FileSizeParamType.compact_value(defaults['max_archive_size_bytes'])}")
@click.option(
    '--min_archive_ratio',
    type=click.FloatRange(0, 1),
    help='Minimum allowed compression ratio for an archive. A floating-point value between 0.0 and 1.0, inclusive. Default is 0.005'
)
@click.version_option(metadata.version("archae"), "-v", "--version")
def cli(archive_path: str, max_total_size_bytes: int, max_archive_size_bytes: int, min_archive_ratio: float) -> None:
    """Archae explodes archives."""
    locate_tools()
    config["max_total_size_bytes"] = max_total_size_bytes
    config["max_archive_size_bytes"] = max_archive_size_bytes
    config["min_archive_ratio"] = min_archive_ratio
    handle_file(Path(archive_path))
    debug_print_tracked_files()


tracked_files: dict[str, dict] = {}
base_dir = Path.cwd()
extract_dir = base_dir / "extracted"
if extract_dir.exists() and extract_dir.is_dir():
    shutil.rmtree(extract_dir)
extract_dir.mkdir(exist_ok=True)

def convert_size_arg(self, value, param, ctx):
    if isinstance(value, int):
        return value
    
    # Regex to split number and unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]B?)$', value, re.IGNORECASE)
    if not match:
        self.fail(f"{value} is not a valid file size (e.g., 10G, 500M)", param, ctx)
    
    number, unit = match.groups()
    number = float(number)
    unit = unit.upper()

    units = {
        'K': 1024,
        'KB': 1024,
        'M': 1024**2,
        'MB': 1024**2,
        'G': 1024**3,
        'GB': 1024**3,
        'T': 1024**4,
        'TB': 1024**4,
    }


def locate_tools() -> None:
    """Locate required external tools."""
    for tool_name in tool_names:
        tool_path = shutil.which(tool_name)
        if tool_path is None:
            pass
        tools[tool_name] = tool_path


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
            extracted_size = get_archive_extracted_size(file_path, base_hash, archiver)
            add_metadata_to_hash(base_hash, "extracted_size", extracted_size)
            compression_ratio = extracted_size / file_size_bytes
            add_metadata_to_hash(base_hash, "overall_compression_ratio", compression_ratio)
            if extracted_size > config["max_archive_size_bytes"]:
                click.echo(f"Skipped archive {file_path} because expected size {extracted_size} is greater than max_archive_size_bytes {config["max_archive_size_bytes"]}")
            elif compression_ratio < config["min_archive_ratio"]:
                click.echo(f"Skipped archive {file_path} because compression ratio {compression_ratio:.5f} is less than min_archive_ratio {config["min_archive_ratio"]}")
            else:
                extraction_dir = extract_archive(file_path, base_hash, archiver)
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

    for mime_type_list in [mime_types_7z, mime_types_pea, mime_types_unar]:
        if mime_type in mime_type_list:
            return True
    for extension_list in [extensions_7z, extensions_pea, extensions_unar]:
        if extension in extension_list:
            return True

    return False


def get_archiver_for_file(hash: str) -> str | None:
    """Determine the appropriate archiver for a file based on its metadata.

    Args:
        hash (str): The hash of the file.

    Returns:
        str | None: The name of the archiver tool if found, otherwise None.
    """
    metadata = get_tracked_file_metadata(hash)
    mime_type = metadata.get("type_mime", "").lower()
    extension = metadata.get("extension", "").lower()

    if "7z" in tools and (mime_type in mime_types_7z or extension in extensions_7z):
        return "7z"
    if "pea" in tools and (mime_type in mime_types_pea or extension in extensions_pea):
        return "pea"
    if "unar" in tools and (
        mime_type in mime_types_unar or extension in extensions_unar
    ):
        return "unar"
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


def extract_archive(archive_path: Path, hash: str, archiver: str) -> Path:
    """Extracts an archive to a specified directory.

    Args:
        archive_path (Path): The path to the archive file.
        hash (str): The hash of the archive file.
        archiver (str): The archiver tool to use for extraction.

    Returns:
        Path: The path to the extracted contents.
    """
    extracted_path = extract_dir / hash
    command: list[str] = []
    archiver_tool: str | None = tools[archiver]
    if archiver_tool is not None:
        if archiver == "7z":
            command = [archiver_tool, "x", str(archive_path), f"-o{extracted_path!s}"]
        elif archiver == "peazip":
            command = [
                archiver_tool,
                "-ext2simple",
                str(archive_path),
                str(extracted_path),
            ]
        elif archiver == "unar":
            command = [archiver_tool, "-o", str(extracted_path), str(archive_path)]
        else:
            click.echo(
                f"Unsupported archiver: {archiver}; this generally shouldn't happen!"
            )

        if command:
            with contextlib.suppress(FileNotFoundError):
                subprocess.run(command, check=True)  # noqa: S603
    else:
        click.echo(
            f"No extraction command for archiver: {archiver}; this generally shouldn't happen!"
        )

    return extracted_path


def get_archive_extracted_size(archive_path: Path, hash: str, archiver: str) -> int:
    """Get the uncompressed size of the contents

    Args:
        archive_path (Path): The path to the archive file.
        hash (str): The hash of the archive file.
        archiver (str): The archiver tool to use for extraction.

    Returns:
        int: The size of the contents
    """
    extracted_path = extract_dir / hash
    command: list[str] = []
    archiver_tool: str | None = tools[archiver]
    if archiver_tool is not None:
        if archiver == "7z":
            command = [archiver_tool, "l", "-slt", str(archive_path)]
        elif archiver == "peazip":
            click.echo(
                f"{archiver} size testing not yet implemented!"
            )
        elif archiver == "unar":
            click.echo(
                f"{archiver} size testing not yet implemented!"
            )
        else:
            click.echo(
                f"Unsupported archiver: {archiver}; this generally shouldn't happen!"
            )

        if command:
            with contextlib.suppress(FileNotFoundError):
                result = subprocess.run(command, check=True, capture_output=True, text=True)  # noqa: S603
                
                ## TODO: Implement for other archivers
                result_lines = str(result.stdout).splitlines()
                exploded_size = 0
                for line in result_lines:
                    if line.startswith("Size = "):
                        exploded_size += int(line[7:])
                return exploded_size

    else:
        click.echo(
            f"No sizing command for archiver: {archiver}; this generally shouldn't happen!"
        )

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
