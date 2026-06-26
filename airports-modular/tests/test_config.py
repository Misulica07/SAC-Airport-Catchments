"""Sanity checks for the config loader.

These tests do not hit the network or the filesystem outside the project
root, so they are safe to run in CI."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config import load_config


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "airports.yaml"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH, project_root=PROJECT_ROOT)


def test_three_airports_are_defined(cfg):
    codes = {a.code for a in cfg.airports}
    assert codes == {"LTN", "LHR", "LGW"}


def test_thresholds_are_in_seconds(cfg):
    assert cfg.isochrones.thresholds_seconds == [
        m * 60 for m in cfg.isochrones.thresholds_minutes
    ]


def test_default_thresholds_respect_ors_free_tier(cfg):
    assert max(cfg.isochrones.thresholds_minutes) <= 60


def test_directories_resolve_under_project_root(cfg):
    assert cfg.raw_dir == PROJECT_ROOT / "data" / "raw"
    assert cfg.processed_dir == PROJECT_ROOT / "data" / "processed"


def test_crs_settings_use_known_codes(cfg):
    assert cfg.crs.geographic == "EPSG:4326"
    assert cfg.crs.projected_uk == "EPSG:27700"
