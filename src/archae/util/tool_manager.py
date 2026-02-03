"""Tool manager for locating and managing external archiving tools."""

from __future__ import annotations

import logging
import shutil
from typing import TYPE_CHECKING, ClassVar, cast

import archae.util.archiver

if TYPE_CHECKING:
    from archae.util.archiver.base_archiver import BaseArchiver

logger = logging.getLogger("archae")


class ToolManager:
    """Manager for locating and managing external archiving tools."""

    __tools: ClassVar[dict[str, BaseArchiver]] = {}

    @classmethod
    def locate_tools(cls) -> None:
        """Locate external tools."""
        for archiver_cls in archae.util.archiver.BaseArchiver.__subclasses__():
            logger.debug("Locating tool for %s", archiver_cls.archiver_name)
            tool_path = shutil.which(str(archiver_cls.executable_name))
            if tool_path:
                logger.debug("Found %s at %s", archiver_cls.archiver_name, tool_path)
                cls.__tools[str(archiver_cls.archiver_name)] = archiver_cls(tool_path)  # type: ignore[abstract]
            else:
                logger.warning(
                    "MISSING_ARCHIVER: Could not find %s; some archive types may not be supported",
                    archiver_cls.archiver_name,
                )

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get a sorted list of all file extensions supported by located tools.

        Returns:
            list[str]: Sorted list of supported file extensions.
        """
        supported: set[str] = set()
        for tool in cls.__tools.values():
            supported.update(tool.file_extensions)
        return sorted(supported)

    @classmethod
    def get_unsupported_extensions(cls) -> list[str]:
        """Get a sorted list of all file extensions from all archiver subclasses that are not currently supported.

        Returns:
            list[str]: Sorted list of unsupported file extensions.
        """
        all_extensions: set[str] = set()
        supported: set[str] = set()

        # Get all extensions from all archiver classes
        for archiver_cls in archae.util.archiver.BaseArchiver.__subclasses__():
            all_extensions.update(cast("list[str]", archiver_cls.file_extensions))

        # Get supported extensions from located tools
        for tool in cls.__tools.values():
            supported.update(tool.file_extensions)

        # Return the difference
        unsupported = all_extensions - supported
        return sorted(unsupported)

    @classmethod
    def get_supported_mime_types(cls) -> list[str]:
        """Get a sorted list of all MIME types supported by located tools.

        Returns:
            list[str]: Sorted list of supported MIME types.
        """
        supported: set[str] = set()
        for tool in cls.__tools.values():
            supported.update(tool.mime_types)
        return sorted(supported)

    @classmethod
    def get_unsupported_mime_types(cls) -> list[str]:
        """Get a sorted list of all MIME types from all archiver subclasses that are not currently supported.

        Returns:
            list[str]: Sorted list of unsupported MIME types.
        """
        all_mime_types: set[str] = set()
        supported: set[str] = set()

        # Get all MIME types from all archiver classes
        for archiver_cls in archae.util.archiver.BaseArchiver.__subclasses__():
            all_mime_types.update(cast("list[str]", archiver_cls.mime_types))

        # Get supported MIME types from located tools
        for tool in cls.__tools.values():
            supported.update(tool.mime_types)

        # Return the difference
        unsupported = all_mime_types - supported
        return sorted(unsupported)

    @classmethod
    def get_tools(cls) -> dict[str, BaseArchiver]:
        """Get a shallow copy of the tools dictionary.

        Returns:
            dict[str, BaseArchiver]: A shallow copy of the tools dictionary.
        """
        return cls.__tools.copy()
