"""Tool manager for locating and managing external archiving tools."""

from __future__ import annotations

import logging
import shutil
from typing import TYPE_CHECKING

import archae.util.archiver

if TYPE_CHECKING:
    from archae.util.archiver.base_archiver import BaseArchiver

logger = logging.getLogger("archae")

tools: dict[str, BaseArchiver] = {}


def locate_tools() -> None:
    """Locate external tools."""
    for cls in archae.util.archiver.BaseArchiver.__subclasses__():
        logger.info("Locating tool for %s", cls.archiver_name)
        tool_path = shutil.which(str(cls.executable_name))
        if tool_path:
            logger.info("Found %s at %s", cls.archiver_name, tool_path)
            tools[str(cls.archiver_name)] = cls(tool_path)  # type: ignore[abstract]
        else:
            logger.warning(
                "MISSING_ARCHIVER: Could not find %s; some archive types may not be supported",
                cls.archiver_name,
            )
