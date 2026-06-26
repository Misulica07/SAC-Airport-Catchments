"""Geospatial helpers.

Why this exists
---------------
Two operations recur across the codebase:

1. Reading and writing GeoJSON / GeoPandas objects with a known CRS.
2. Computing area-weighted aggregates after a spatial overlay.

Centralising them avoids subtle bugs (e.g. computing distances in degrees
because someone forgot to project) and keeps the analysis code declarative.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import shape


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def read_geojson(path: str | Path, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Read a GeoJSON file and tag it with an explicit CRS.

    OpenRouteService and the ONS Geoportal occasionally emit GeoJSON without
    the ``crs`` block, so we set it defensively rather than trust the file.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return gpd.GeoDataFrame.from_features(payload["features"], crs=crs)


def write_geojson(gdf: gpd.GeoDataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")


# ---------------------------------------------------------------------------
# Projections
# ---------------------------------------------------------------------------


def to_projected(gdf: gpd.GeoDataFrame, projected_crs: str = "EPSG:27700") -> gpd.GeoDataFrame:
    """Reproject to a projected CRS (default British National Grid) for accurate
    area and distance computations in metres.
    """
    return gdf.to_crs(projected_crs)


def to_geographic(gdf: gpd.GeoDataFrame, geographic_crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Reproject back to WGS-84 for display in folium."""
    return gdf.to_crs(geographic_crs)


# ---------------------------------------------------------------------------
# Area-weighted aggregation
# ---------------------------------------------------------------------------


def area_weight(
    overlay: gpd.GeoDataFrame,
    area_total_col: str = "area_total_m2",
) -> gpd.GeoDataFrame:
    """Attach an ``area_weight`` column to an overlay GeoDataFrame.

    Expected input: result of ``gpd.overlay(small_polygons, big_polygons)``
    in a projected CRS, with ``area_total_col`` precomputed on the small
    polygons before the overlay.

    Returns the same GeoDataFrame with ``area_weight = area_intersected /
    area_total``. Use this as a multiplier when aggregating extensive
    variables (population, dwellings) that should not be double-counted when
    a polygon straddles two isochrones.
    """
    out = overlay.copy()
    out["area_intersected_m2"] = out.geometry.area
    out["area_weight"] = out["area_intersected_m2"] / out[area_total_col]
    return out
