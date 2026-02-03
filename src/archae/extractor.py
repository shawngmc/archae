"""Archive extraction module for archae."""

from __future__ import annotations

import hashlib
import logging
import shutil
from typing import TYPE_CHECKING

import magic

from archae.config import apply_options, get_default_settings, get_settings
from archae.util.file_tracker import FileTracker
from archae.util.tool_manager import ToolManager

if TYPE_CHECKING:
    from pathlib import Path

    from archae.util.archiver.base_archiver import BaseArchiver


class WarningAccumulator(logging.Handler):
    """Logging handler to accumulate warnings while still printing them."""

    def __init__(self) -> None:
        """Initialize the WarningAccumulator."""
        super().__init__()
        self.warnings: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Print and accumulate warning messages."""
        if record.levelno >= logging.WARNING:
            self.warnings.append(self.format(record))
        print(self.format(record))  # noqa: T201


logger = logging.getLogger("archae")
logger.setLevel(logging.INFO)
accumulator = WarningAccumulator()
logger.addHandler(accumulator)
logger.setLevel(logging.DEBUG)


class ArchiveExtractor:
    """Handles archive extraction and file tracking."""

    def __init__(self, extract_dir: Path) -> None:
        """Initialize the ArchiveExtractor.

        Args:
            extract_dir (Path): The base directory for extraction. Defaults to current working directory + extracted.
        """
        self.extract_dir = extract_dir
        if self.extract_dir.exists() and self.extract_dir.is_dir():
            shutil.rmtree(self.extract_dir)
        self.extract_dir.mkdir(exist_ok=True)
        self.file_tracker = FileTracker()
        if ToolManager.get_tools() == {}:
            ToolManager.locate_tools()

    def handle_file(self, file_path: Path) -> None:
        """Handle a file given its path.

        Args:
            file_path (Path): The path to the file.
        """
        self.__handle_file(file_path)

    def __handle_file(self, file_path: Path, depth: int = 1) -> None:
        """Internal implementation of handle_file.

        Args:
            file_path (Path): The path to the file.
            depth (int): The current depth in the archive extraction tree. Defaults to 1.
        """
        logger.info("Starting examination of file: %s", file_path)

        base_hash = self._sha256_hash_file(file_path)
        file_size_bytes = file_path.stat().st_size
        self.file_tracker.track_file(base_hash, file_size_bytes)
        self.file_tracker.track_file_path(base_hash, file_path)
        self.file_tracker.add_metadata_to_hash(
            base_hash, "type", magic.from_file(file_path)
        )
        self.file_tracker.add_metadata_to_hash(
            base_hash, "type_mime", magic.from_file(file_path, mime=True)
        )
        extension = file_path.suffix.lstrip(".").lower()
        self.file_tracker.add_metadata_to_hash(base_hash, "extension", extension)
        is_file_archive = self._is_archive(base_hash)
        self.file_tracker.add_metadata_to_hash(base_hash, "is_archive", is_file_archive)
        if is_file_archive:
            settings_dict = get_settings()
            if settings_dict["MAX_DEPTH"] == 0 or depth < settings_dict["MAX_DEPTH"]:
                archiver = self._get_archiver_for_file(base_hash)
                if archiver:
                    extracted_size = archiver.get_archive_uncompressed_size(file_path)
                    self.file_tracker.add_metadata_to_hash(
                        base_hash, "extracted_size", extracted_size
                    )
                    compression_ratio = extracted_size / file_size_bytes
                    self.file_tracker.add_metadata_to_hash(
                        base_hash, "overall_compression_ratio", compression_ratio
                    )
                    if extracted_size > settings_dict["MAX_ARCHIVE_SIZE_BYTES"]:
                        logger.warning(
                            "MAX_ARCHIVE_SIZE_BYTES: Skipped archive %s because expected size %s is greater than MAX_ARCHIVE_SIZE_BYTES %s",
                            file_path,
                            extracted_size,
                            settings_dict["MAX_ARCHIVE_SIZE_BYTES"],
                        )
                    elif (
                        self.file_tracker.get_tracked_file_size() + extracted_size
                        > settings_dict["MAX_TOTAL_SIZE_BYTES"]
                    ):
                        logger.warning(
                            "MAX_TOTAL_SIZE_BYTES: Skipped archive %s because expected size %s + current tracked files %s is greater than MAX_TOTAL_SIZE_BYTES %s",
                            file_path,
                            extracted_size,
                            self.file_tracker.get_tracked_file_size(),
                            settings_dict["MAX_TOTAL_SIZE_BYTES"],
                        )
                    elif compression_ratio < settings_dict["MIN_ARCHIVE_RATIO"]:
                        logger.warning(
                            "MIN_ARCHIVE_RATIO: Skipped archive %s because compression ratio %.5f is less than MIN_ARCHIVE_RATIO %s",
                            file_path,
                            compression_ratio,
                            settings_dict["MIN_ARCHIVE_RATIO"],
                        )
                    elif (
                        shutil.disk_usage(self.extract_dir).free - extracted_size
                        < settings_dict["MIN_DISK_FREE_SPACE"]
                    ):
                        logger.warning(
                            "MIN_DISK_FREE_SPACE:Skipped archive %s because extracting it would leave less than MIN_DISK_FREE_SPACE %s bytes free at extraction location %s",
                            file_path,
                            settings_dict["MIN_DISK_FREE_SPACE"],
                            self.extract_dir,
                        )
                    else:
                        extraction_dir = self.extract_dir / base_hash
                        archiver.extract_archive(file_path, extraction_dir)
                        child_files = self._list_child_files(extraction_dir)
                        for child_file in child_files:
                            self.__handle_file(child_file, depth + 1)
                else:
                    logger.warning(
                        "NO_ARCHIVER: No suitable archiver found for file: %s",
                        file_path,
                    )
            else:
                logger.warning(
                    "MAX_DEPTH: File %s is not extracted; max depth reached.", file_path
                )

    def _is_archive(self, file_hash: str) -> bool:
        """Determine the appropriate archiver for a file based on its metadata.

        Args:
            file_hash (str): The hash of the file.

        Returns:
            bool: True if the file is an archive, otherwise False.

        """
        metadata = self.file_tracker.get_tracked_file_metadata(file_hash)
        mime_type = metadata.get("type_mime", "").lower()
        extension = metadata.get("extension", "").lower()

        for tool in ToolManager.get_tools().values():
            if mime_type in tool.mime_types or extension in tool.file_extensions:
                return True

        return False

    def _get_archiver_for_file(self, file_hash: str) -> BaseArchiver | None:
        """Determine the appropriate archiver for a file based on its metadata.

        Args:
            file_hash (str): The hash of the file.

        Returns:
            str | None: The name of the archiver tool if found, otherwise None.
        """
        metadata = self.file_tracker.get_tracked_file_metadata(file_hash)
        mime_type = metadata.get("type_mime", "").lower()
        extension = metadata.get("extension", "").lower()

        for tool in ToolManager.get_tools().values():
            if mime_type in tool.mime_types or extension in tool.file_extensions:
                return tool
        return None

    @staticmethod
    def _list_child_files(directory_path: Path, pattern: str = "*") -> list[Path]:
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

    @staticmethod
    def _sha256_hash_file(file_path: Path) -> str:
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

    def get_tracked_files(self) -> dict[str, dict]:
        """Print the tracked files for debugging purposes."""
        return self.file_tracker.get_tracked_files()

    def get_warnings(self) -> list[str]:
        """Print accumulated warnings for debugging purposes."""
        return accumulator.warnings

    def get_default_settings(self) -> dict:
        """Get the default settings from the config module.

        Returns:
            dict: Dictionary of default settings.
        """
        return get_default_settings()

    def apply_settings(self, option_list: list[tuple[str, str]]) -> None:
        """Apply a list of settings options.

        Args:
            option_list (list[tuple[str, str]]): List of (key, value) tuples to apply.

        Example:
            extractor.apply_settings([("MAX_ARCHIVE_SIZE_BYTES", "5000000000")])
        """
        apply_options(option_list)
