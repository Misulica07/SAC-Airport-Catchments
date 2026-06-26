"""Centralised logging configuration.

Why this exists
---------------
Every module needs logging, but doing ``logging.basicConfig`` in each one leads
to duplicated handlers and inconsistent formatting. This helper is called once
at the start of every entry point and produces a single, well-formatted stream.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Install a single root logger writing to stdout in a readable format."""
    root = logging.getLogger()
    if root.handlers:
        # Idempotent: prevents double handlers when invoked from notebooks.
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Convenience wrapper so callers don't import the stdlib themselves."""
    return logging.getLogger(name)
