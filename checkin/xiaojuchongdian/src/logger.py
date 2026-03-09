"""Logging helper for Xiaoju check-in runner."""

from __future__ import annotations

import logging
import os
import sys

_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def configure_logging() -> None:
    level_name = os.getenv("DAILYHUB_LOG_LEVEL", "INFO").upper()
    if level_name not in _VALID_LEVELS:
        print(
            f"WARNING: DAILYHUB_LOG_LEVEL={level_name!r} is not a valid log level. "
            f"Valid values: {', '.join(sorted(_VALID_LEVELS))}. Defaulting to INFO.",
            file=sys.stderr,
        )
        level_name = "INFO"
    level = getattr(logging, level_name)
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    else:
        root.setLevel(level)
