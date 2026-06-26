"""UK Census ingestion (Phase 2 — skeleton).

Two data sources are wrapped here:

1. **Spatial boundaries** (LSOA / MSOA / ITL3) from the ONS Geography Portal.
2. **Tabular indicators** (population, age, IMD) from the Nomis API at
   https://www.nomisweb.co.uk/.

The Nomis API is open and does not require an API key; we still pass a
descriptive ``User-Agent`` so the ONS can identify the traffic.

Implementation is intentionally TODO. The class signatures and docstrings
fix the contract so the rest of the pipeline can be wired up in advance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd

from src.config import CensusSettings
from src.ingestion.base import BaseIngester


class CensusIngester(BaseIngester):
    """Download ONS Census boundaries and Nomis tables."""

    api_key_env = None  # Nomis is open; no key required.
    NOMIS_BASE_URL = "https://www.nomisweb.co.uk/api/v01/dataset"

    def __init__(self, output_dir: str | Path, settings: CensusSettings) -> None:
        super().__init__(output_dir=output_dir)
        self.settings = settings

    # ------------------------------------------------------------------
    # BaseIngester implementation
    # ------------------------------------------------------------------

    def fetch(self, table_code: str | None = None) -> Any:  # type: ignore[override]
        """Fetch either a boundary set (when ``table_code`` is None) or a Nomis table."""
        if table_code is None:
            return self.fetch_boundaries(self.settings.geography_level)
        return self.fetch_table(table_code, self.settings.geography_level)

    def save(self, payload: Any, name: str) -> Path:  # type: ignore[override]
        path = self.output_dir / f"{name}.parquet"
        # GeoDataFrames support to_parquet via pyarrow.
        payload.to_parquet(path)
        self.log.info("Saved %s", path.relative_to(path.parents[2]))
        return path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_boundaries(self, level: str) -> gpd.GeoDataFrame:
        """Download the ONS boundary file for the requested geography level.

        Returns
        -------
        gpd.GeoDataFrame
            Geometries in EPSG:27700 (British National Grid) with at least
            the columns ``GEOGRAPHY_CODE`` and ``GEOGRAPHY_NAME``.

        Notes
        -----
        TODO Phase 2 — implement using ``geopandas.read_file`` against the
        ONS Geography Portal URL pattern. Cache the result in ``data/raw``
        so subsequent runs do not re-download.
        """
        raise NotImplementedError("Phase 2 — implement against ONS Geography Portal.")

    def fetch_table(self, table_code: str, geography_level: str) -> Any:
        """Download a Nomis table at the requested geography level.

        Parameters
        ----------
        table_code
            Nomis dataset identifier, e.g. ``TS001`` for residents total.
        geography_level
            One of ``LSOA``, ``MSOA``, ``ITL3``.

        Returns
        -------
        pandas.DataFrame keyed on the same code column as :meth:`fetch_boundaries`.

        Notes
        -----
        TODO Phase 2 — wrap https://www.nomisweb.co.uk/api/v01/dataset and
        translate geography_level into Nomis ``geography`` query codes.
        """
        raise NotImplementedError("Phase 2 — implement Nomis client.")
