"""Data acquisition layer.

Each module in this package is responsible for fetching one external data
source and writing the raw payload to ``data/raw/``. They never perform
analysis — that lives in :mod:`src.analysis`.
"""

from .base import BaseIngester
from .isochrones import IsochroneIngester

__all__ = ["BaseIngester", "IsochroneIngester"]
