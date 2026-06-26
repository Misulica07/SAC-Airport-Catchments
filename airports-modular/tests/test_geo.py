"""Unit tests for the geospatial helpers."""

from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import Polygon

from src.utils.geo import area_weight, to_geographic, to_projected


@pytest.fixture
def square_polygon_4326() -> gpd.GeoDataFrame:
    """A 1-degree square centred on London — only for CRS round-trips."""
    poly = Polygon([(-0.5, 51.0), (0.5, 51.0), (0.5, 52.0), (-0.5, 52.0)])
    return gpd.GeoDataFrame({"id": [1]}, geometry=[poly], crs="EPSG:4326")


def test_crs_roundtrip_returns_to_origin(square_polygon_4326):
    projected = to_projected(square_polygon_4326)
    back = to_geographic(projected)
    assert square_polygon_4326.crs == back.crs
    assert square_polygon_4326.geometry.iloc[0].equals_exact(
        back.geometry.iloc[0], tolerance=1e-6
    )


def test_area_weight_handles_full_overlap():
    poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    gdf = gpd.GeoDataFrame(
        {"area_total_m2": [100.0]}, geometry=[poly], crs="EPSG:27700"
    )
    out = area_weight(gdf)
    assert out["area_weight"].iloc[0] == pytest.approx(1.0)


def test_area_weight_handles_half_overlap():
    half = Polygon([(0, 0), (5, 0), (5, 10), (0, 10)])
    gdf = gpd.GeoDataFrame(
        {"area_total_m2": [100.0]}, geometry=[half], crs="EPSG:27700"
    )
    out = area_weight(gdf)
    assert out["area_weight"].iloc[0] == pytest.approx(0.5)
