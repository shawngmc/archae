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
from archae.util.lists import skip_delete_extensions, skip_delete_mimetypes


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

    def clear_warnings(self) -> None:
        """Clear the accumulated warnings."""
        self.warnings.clear()


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
        accumulator.clear_warnings()
        self.file_tracker.reset_tracked_files()
        self._handle_file(file_path)

    def _handle_file(self, file_path: Path, depth: int = 1) -> None:
        """Internal implementation of handle_file.

        Args:
            file_path (Path): The path to the file.
            depth (int): The current depth in the archive extraction tree. Defaults to 1.
        """
        logger.info("Starting examination of file: %s", file_path)

        base_hash = self._sha256_hash_file(file_path)
        self._track_file_metadata(base_hash, file_path)

        is_file_archive = self._is_archive(base_hash)
        self.file_tracker.add_metadata(base_hash, "is_archive", is_file_archive)

        if is_file_archive:
            self._process_archive(base_hash, file_path, depth)

    def _track_file_metadata(self, base_hash: str, file_path: Path) -> None:
        """Track file size and metadata including type, mime type, and extension.

        Args:
            base_hash (str): The SHA-256 hash of the file.
            file_path (Path): The path to the file.
        """
        file_size_bytes = file_path.stat().st_size
        self.file_tracker.track_file(base_hash, file_size_bytes)
        self.file_tracker.track_file_path(base_hash, file_path)
        self.file_tracker.add_metadata(base_hash, "type", magic.from_file(file_path))
        self.file_tracker.add_metadata(
            base_hash, "type_mime", magic.from_file(file_path, mime=True)
        )
        extension = file_path.suffix.lstrip(".").lower()
        self.file_tracker.add_metadata(base_hash, "extension", extension)

    def _get_uncompressed_size(
        self, file_path: Path, archiver: BaseArchiver
    ) -> int | None:
        """Retrieve the uncompressed size of an archive.

        Args:
            base_hash (str): The SHA-256 hash of the file.
            file_path (Path): The path to the archive file.
            archiver (BaseArchiver): The archiver to use for size retrieval.

        Returns:
            int | None: The uncompressed size in bytes, or None if retrieval failed.
        """
        try:
            return archiver.get_archive_uncompressed_size(file_path)
        except NotImplementedError:
            logger.warning(
                "SIZE_RETRIEVAL_FAILED: No archiver supports analysis for %s; extraction will continue",
                file_path,
            )
        except RuntimeError as e:
            logger.warning(
                "SIZE_RETRIEVAL_FAILED: Could not retrieve size for archive %s: %s",
                file_path,
                str(e),
            )
        return None

    def _process_archive(self, base_hash: str, file_path: Path, depth: int) -> None:
        """Process an archive file: validate depth, retrieve size, and extract if appropriate.

        Args:
            base_hash (str): The SHA-256 hash of the archive file.
            file_path (Path): The path to the archive file.
            depth (int): The current depth in the archive extraction tree.
        """
        settings_dict = get_settings()

        # Check if we've reached maximum depth
        if settings_dict["MAX_DEPTH"] != 0 and depth >= settings_dict["MAX_DEPTH"]:
            logger.warning(
                "MAX_DEPTH: File %s is not extracted; max depth reached.", file_path
            )
            return

        # Get the appropriate archiver for this file
        archiver = self._get_archiver_for_file(base_hash)
        if not archiver:
            logger.warning(
                "NO_ARCHIVER: No suitable archiver found for file: %s",
                file_path,
            )
            return

        # Retrieve archive size and calculate compression ratio
        extracted_size = self._get_uncompressed_size(file_path, archiver)
        if extracted_size is None:
            return

        self.file_tracker.add_metadata(base_hash, "extracted_size", extracted_size)
        compression_ratio = (
            extracted_size / self.file_tracker.get_file_size(base_hash)
            if self.file_tracker.get_file_size(base_hash) > 0
            else 0
        )
        self.file_tracker.add_metadata(
            base_hash, "overall_compression_ratio", compression_ratio
        )

        # Check if extraction should proceed based on settings
        if not self._should_extract_archive(base_hash, file_path):
            return

        # Extract the archive and process contained files
        if not self._extract_archive(archiver, file_path, base_hash):
            return

        extraction_dir = self.extract_dir / base_hash
        child_files = self._list_child_files(extraction_dir)
        for child_file in child_files:
            self._handle_file(child_file, depth + 1)

        self._cleanup(file_path, base_hash)

    def _extract_archive(
        self, archiver: BaseArchiver, file_path: Path, base_hash: str
    ) -> bool:
        """Extract an archive file to the extraction directory.

        Args:
            archiver (BaseArchiver): The archiver to use for extraction.
            file_path (Path): The path to the archive file.
            base_hash (str): The SHA-256 hash of the archive file.

        Returns:
            bool: True if extraction succeeded, False otherwise.
        """
        try:
            extraction_dir = self.extract_dir / base_hash
            logger.info(
                "Extracting archive %s to %s",
                file_path,
                extraction_dir,
            )
            archiver.extract_archive(file_path, extraction_dir)
        except RuntimeError as e:
            logger.warning(
                "EXTRACTION_FAILED: Extraction failed for archive %s: %s",
                file_path,
                str(e),
            )
            return False
        else:
            return True

    def _cleanup(self, file_path: Path, base_hash: str) -> None:
        """Handle any cleanup actions such as deleting the archive if settings dictate.

        Args:
            file_path (Path): The path to the original archive file.
            base_hash (str): The hash of the original archive file.
        """
        if self._should_delete_archive(base_hash, file_path):
            try:
                file_path.unlink()
                self.file_tracker.add_metadata(base_hash, "deleted", True)  # noqa: FBT003
                logger.info(
                    "Deleted archive %s after extraction as per settings.",
                    file_path,
                )
            except (PermissionError, OSError) as e:
                logger.warning(
                    "DELETE_FAILED: Could not delete archive %s after extraction: %s",
                    file_path,
                    str(e),
                )

    def _is_archive(self, file_hash: str) -> bool:
        """Determine the appropriate archiver for a file based on its metadata.

        Args:
            file_hash (str): The hash of the file.

        Returns:
            bool: True if the file is an archive, otherwise False.

        """
        metadata = self.file_tracker.get_file_metadata(file_hash)
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
        metadata = self.file_tracker.get_file_metadata(file_hash)
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

    def apply_options(self, option_list: dict[str, str | int | float | bool]) -> None:
        """Apply a dict of options.

        Args:
            option_list (dict[str, str | int | float | bool]): Dictionary of options to apply.

        Example:
            extractor.apply_options({"MAX_ARCHIVE_SIZE_BYTES": "5000000000"})
        """
        apply_options(option_list)

    def _should_extract_archive(self, file_hash: str, file_path: Path) -> bool:
        """Determine whether an archive should be extracted based on its metadata and current settings."""
        settings_dict = get_settings()
        metadata = self.file_tracker.get_file_metadata(file_hash)
        extracted_size = metadata.get("extracted_size", 0)
        if extracted_size > settings_dict["MAX_ARCHIVE_SIZE_BYTES"]:
            logger.warning(
                "MAX_ARCHIVE_SIZE_BYTES: Skipped archive %s because expected size %s is greater than MAX_ARCHIVE_SIZE_BYTES %s",
                file_path,
                extracted_size,
                settings_dict["MAX_ARCHIVE_SIZE_BYTES"],
            )
            return False

        total_extracted = self.file_tracker.get_total_tracked_file_size()
        if total_extracted + extracted_size > settings_dict["MAX_TOTAL_SIZE_BYTES"]:
            logger.warning(
                "MAX_TOTAL_SIZE_BYTES: Skipped archive %s because expected size %s + current tracked files %s is greater than MAX_TOTAL_SIZE_BYTES %s",
                file_path,
                extracted_size,
                total_extracted,
                settings_dict["MAX_TOTAL_SIZE_BYTES"],
            )
            return False
        compression_ratio = metadata.get("overall_compression_ratio", 0)
        if compression_ratio < settings_dict["MIN_ARCHIVE_RATIO"]:
            logger.warning(
                "MIN_ARCHIVE_RATIO: Skipped archive %s because compression ratio %.5f is less than MIN_ARCHIVE_RATIO %s",
                file_path,
                compression_ratio,
                settings_dict["MIN_ARCHIVE_RATIO"],
            )
            return False
        if (
            shutil.disk_usage(self.extract_dir).free - extracted_size
            < settings_dict["MIN_DISK_FREE_SPACE"]
        ):
            logger.warning(
                "MIN_DISK_FREE_SPACE: Skipped archive %s because extracting it would leave less than MIN_DISK_FREE_SPACE %s bytes free at extraction location %s",
                file_path,
                settings_dict["MIN_DISK_FREE_SPACE"],
                self.extract_dir,
            )
            return False
        return True

    def _should_delete_archive(self, file_hash: str, file_path: Path) -> bool:
        """Determine whether an archive should be deleted after extraction based on its metadata and current settings."""
        settings_dict = get_settings()
        if not settings_dict["DELETE_ARCHIVES_AFTER_EXTRACTION"]:
            return False

        metadata = self.file_tracker.get_file_metadata(file_hash)
        extension = metadata.get("extension", "").lower()
        if extension in skip_delete_extensions:
            logger.warning(
                "SKIP_DELETE_EXTENSION: Archive %s not deleted after extraction due to its extension '%s' being in the skip list.",
                file_path,
                extension,
            )
            return False

        mime_type = metadata.get("type_mime", "").lower()
        if mime_type in skip_delete_mimetypes:
            logger.warning(
                "SKIP_DELETE_MIMETYPE: Archive %s not deleted after extraction due to its mime type '%s' being in the skip list.",
                file_path,
                mime_type,
            )
            return False

        return True
