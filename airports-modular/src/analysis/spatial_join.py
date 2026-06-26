"""Catchment-area spatial joins (Phase 2 — skeleton + helpers).

The analytical core of the project. Once the Census ingester is online,
this module produces the canonical *catchment table*:

+-----------+------------+----------------------+---------------+-----------+
| airport   | threshold  | demographic indicator| raw value     | area_wt   |
+-----------+------------+----------------------+---------------+-----------+
| LHR       | 30         | population_2021      | 1 482 311     | 0.94      |
| LHR       | 30         | imd_avg              | 18.4          | 0.94      |
| ...                                                                       |

The non-trivial step is area-weighting: an LSOA that straddles the boundary
of two isochrones contributes proportionally to each, rather than being
counted twice.
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd

from src.utils.geo import area_weight, to_projected
from src.utils.logging import get_logger

log = get_logger(__name__)


def overlay_isochrones_with_geography(
    isochrones: gpd.GeoDataFrame,
    geography: gpd.GeoDataFrame,
    projected_crs: str = "EPSG:27700",
) -> gpd.GeoDataFrame:
    """Intersect isochrones with a geography (e.g. LSOAs).

    The function:

    1. Projects both inputs to ``projected_crs`` for accurate areas.
    2. Pre-computes the *total* area of each geography polygon.
    3. Runs ``gpd.overlay(..., how='intersection')``.
    4. Adds an ``area_weight`` column on the result.

    Parameters
    ----------
    isochrones
        GeoDataFrame with at least ``airport_code`` and ``value`` (the
        threshold in minutes) columns.
    geography
        GeoDataFrame for the demographic unit (LSOA / MSOA / ITL3).

    Returns
    -------
    GeoDataFrame in ``projected_crs`` with one row per (airport, threshold,
    geography) intersection plus an ``area_weight`` column.
    """
    log.info(
        "Overlaying %d isochrones with %d geographies", len(isochrones), len(geography)
    )

    iso = to_projected(isochrones, projected_crs)
    geo = to_projected(geography, projected_crs).copy()
    geo["area_total_m2"] = geo.geometry.area

    overlay = gpd.overlay(iso, geo, how="intersection", keep_geom_type=True)
    overlay = area_weight(overlay)

    log.info("Overlay produced %d rows", len(overlay))
    return overlay


def aggregate_population(
    overlay: gpd.GeoDataFrame,
    population_col: str = "population",
) -> pd.DataFrame:
    """Sum area-weighted population per (airport, threshold)."""
    overlay = overlay.copy()
    overlay["population_weighted"] = overlay[population_col] * overlay["area_weight"]
    return (
        overlay.groupby(["airport_code", "value"], as_index=False)
        .agg(population=("population_weighted", "sum"))
        .sort_values(["airport_code", "value"])
    )


def aggregate_deprivation(
    overlay: gpd.GeoDataFrame,
    imd_col: str = "imd_score",
    weight_col: str = "population_weighted",
) -> pd.DataFrame:
    """Population-weighted average IMD score per (airport, threshold)."""
    overlay = overlay.copy()
    overlay["_w_imd"] = overlay[imd_col] * overlay[weight_col]
    grouped = overlay.groupby(["airport_code", "value"], as_index=False).agg(
        sum_w_imd=("_w_imd", "sum"),
        sum_w=(weight_col, "sum"),
    )
    grouped["imd_avg"] = grouped["sum_w_imd"] / grouped["sum_w"]
    return grouped[["airport_code", "value", "imd_avg"]]
