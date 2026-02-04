"""File tracking utilities for archae."""

from __future__ import annotations

import copy
from typing import Any


class FileTracker:
    """Manages file tracking by hash with metadata and paths."""

    def __init__(self) -> None:
        """Initialize the FileTracker."""
        self.tracked_files: dict[str, dict] = {}

    def track_file(self, file_hash: str, file_size_bytes: int) -> None:
        """Track a file by its hash.

        Args:
            file_hash (str): The hash of the file to track.
            file_size_bytes (int): The size of the file in bytes.
        """
        if file_hash not in self.tracked_files:
            self.tracked_files[file_hash] = {}
            self.tracked_files[file_hash]["size"] = file_size_bytes
            self.tracked_files[file_hash]["metadata"] = {}
        elif self.tracked_files[file_hash]["size"] != file_size_bytes:
            msg = f"Hash collision detected for hash {file_hash} with differing sizes."
            raise RuntimeError(msg)

    def is_file_tracked(self, file_hash: str) -> bool:
        """Check if a file is tracked by its hash.

        Args:
            file_hash (str): The hash of the file to check.

        Returns:
            bool: True if the file is tracked, False otherwise.
        """
        return file_hash in self.tracked_files

    def get_file_size(self, file_hash: str) -> int:
        """Get the size for a tracked file by its hash.

        Args:
            file_hash (str): The hash of the file.

        Returns:
            int: The size of the tracked file.
        """
        return self.tracked_files.get(file_hash, {}).get("size", 0)

    def get_file_metadata(self, file_hash: str) -> dict:
        """Get metadata for a tracked file by its hash.

        Args:
            file_hash (str): The hash of the file.

        Returns:
            dict: The metadata of the tracked file.
        """
        return copy.deepcopy(self.tracked_files.get(file_hash, {}).get("metadata", {}))

    def track_file_path(self, file_hash: str, file_path: Any) -> None:
        """Track a file path by its hash.

        Args:
            file_hash (str): The hash of the file.
            file_path: The path to track.
        """
        if "paths" not in self.tracked_files[file_hash]:
            self.tracked_files[file_hash]["paths"] = []

        if file_path not in self.tracked_files[file_hash]["paths"]:
            self.tracked_files[file_hash]["paths"].append(file_path)

    def add_metadata(self, file_hash: str, key: str, value: Any) -> None:
        """Add metadata to a tracked file.

        Args:
            file_hash (str): The hash of the file.
            key (str): The metadata key.
            value (Any): The metadata value.
        """
        self.tracked_files[file_hash]["metadata"][key] = value

    def get_total_tracked_file_size(self) -> int:
        """Get the total size of all tracked files.

        Returns:
            int: The total size in bytes.
        """
        return sum(
            self.tracked_files[file_hash].get("size", 0)
            for file_hash in self.tracked_files
        )

    def get_tracked_files(self) -> dict[str, dict]:
        """Get all tracked files. This is a deep copy to prevent external modification.

        Returns:
            dict[str, dict]: The tracked files dictionary.
        """
        return copy.deepcopy(self.tracked_files)

    def reset_tracked_files(self) -> None:
        """Reset the tracked files."""
        self.tracked_files = {}
