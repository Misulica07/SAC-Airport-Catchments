"""Typed configuration loader.

Why this exists
---------------
Hard-coded paths and magic numbers scattered through the codebase make every
change risky. Centralising the configuration in a single YAML file plus a
small dataclass layer gives the caller a typed, autocompleted view of the
parameters and makes it trivial to swap presets (dev vs full run, free-tier
vs paid ORS quota, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Dataclasses — one per logical section of the YAML.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Airport:
    code: str
    name: str
    lon: float
    lat: float
    colour: str = "blue"


@dataclass(frozen=True)
class IsochroneSettings:
    profile: str
    thresholds_minutes: list[int]
    smoothing: int = 25
    request_timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff_seconds: int = 5

    @property
    def thresholds_seconds(self) -> list[int]:
        return [m * 60 for m in self.thresholds_minutes]


@dataclass(frozen=True)
class MapSettings:
    centre_lat: float
    centre_lon: float
    zoom_start: int = 9
    tiles: str = "CartoDB positron"
    fill_opacity: float = 0.15
    line_weight: int = 2


@dataclass(frozen=True)
class CRSSettings:
    geographic: str = "EPSG:4326"
    projected_uk: str = "EPSG:27700"


@dataclass(frozen=True)
class CensusSettings:
    geography_level: str
    tables: dict[str, str]
    boundaries_url: str


@dataclass(frozen=True)
class TransitSettings:
    tfl_api_root: str
    traveline_gtfs_url: str
    modes: list[str]


@dataclass(frozen=True)
class Config:
    airports: list[Airport]
    isochrones: IsochroneSettings
    map: MapSettings
    crs: CRSSettings
    census: CensusSettings
    transit: TransitSettings
    project_root: Path = field(repr=False)

    # Helpful pre-computed paths so the rest of the codebase never re-derives them.
    @property
    def raw_dir(self) -> Path:
        return self.project_root / "data" / "raw"

    @property
    def interim_dir(self) -> Path:
        return self.project_root / "data" / "interim"

    @property
    def processed_dir(self) -> Path:
        return self.project_root / "data" / "processed"


# ---------------------------------------------------------------------------
# Loader.
# ---------------------------------------------------------------------------


def load_config(
    config_path: str | Path = "config/airports.yaml",
    project_root: str | Path | None = None,
) -> Config:
    """Read the YAML config and return a typed :class:`Config` instance.

    Also loads environment variables from a sibling ``.env`` file if present,
    so any module can read ``os.environ["ORS_API_KEY"]`` without a separate
    bootstrap step.
    """
    project_root = Path(project_root or Path(config_path).resolve().parent.parent)
    load_dotenv(project_root / ".env")

    raw = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))

    return Config(
        airports=[Airport(**a) for a in raw["airports"]],
        isochrones=IsochroneSettings(**raw["isochrones"]),
        map=MapSettings(
            centre_lat=raw["map"]["centre"]["lat"],
            centre_lon=raw["map"]["centre"]["lon"],
            zoom_start=raw["map"]["zoom_start"],
            tiles=raw["map"]["tiles"],
            fill_opacity=raw["map"]["fill_opacity"],
            line_weight=raw["map"]["line_weight"],
        ),
        crs=CRSSettings(**raw["crs"]),
        census=CensusSettings(**raw["census"]),
        transit=TransitSettings(**raw["transit"]),
        project_root=project_root,
    )
