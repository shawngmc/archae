"""Base archiver class for extraction tools."""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import ClassVar


class BaseArchiver(ABC):
    """Base class for archiver/extractor tools."""

    file_extensions: ClassVar[list[str]] = []
    mime_types: ClassVar[list[str]] = []
    archiver_name: str = ""
    executable_name: str = ""

    @property
    def extensions(self) -> list[str]:
        """Get a copy of the supported file extensions."""
        return deepcopy(self.file_extensions)

    @property
    def types(self) -> list[str]:
        """Get a copy of the supported mime types."""
        return deepcopy(self.mime_types)

    @property
    def name(self) -> str:
        """Get the archiver name."""
        return self.archiver_name

    @property
    def executable(self) -> str:
        """Get the executable name."""
        return self.executable_name

    @abstractmethod
    def extract_archive(self) -> None:
        """Extract the archive."""

    @abstractmethod
    def get_archive_uncompressed_size(self) -> int:
        """Get the uncompressed size of the archive."""
