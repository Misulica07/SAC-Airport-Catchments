"""Folium map generators.

Migrated from the original ``visualization.create_multi_airport_map``
function. Wrapped in a class so the caller can add layers incrementally
(isochrones first, then Census choropleths, then transit stops) without
re-reading the GeoJSON files for each layer.
"""

from __future__ import annotations

import json
from pathlib import Path

import folium

from src.config import Airport, Config
from src.utils.logging import get_logger


class CatchmentMap:
    """Composable folium map for the airport catchment analysis."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.log = get_logger(self.__class__.__name__)
        self.map = folium.Map(
            location=[config.map.centre_lat, config.map.centre_lon],
            zoom_start=config.map.zoom_start,
            tiles=config.map.tiles,
        )

    # ------------------------------------------------------------------
    # Layers
    # ------------------------------------------------------------------

    def add_isochrones(self, raw_dir: str | Path | None = None) -> "CatchmentMap":
        """Add one GeoJSON layer per airport found under ``raw_dir``."""
        raw_dir = Path(raw_dir or self.config.raw_dir)
        airport_lookup = {a.code: a for a in self.config.airports}

        for geojson_path in sorted(raw_dir.glob("*_isochrones.geojson")):
            code = geojson_path.stem.split("_")[0]
            airport = airport_lookup.get(code)
            if airport is None:
                self.log.warning("Found %s but no airport %s in config", geojson_path.name, code)
                continue

            self._add_isochrone_layer(geojson_path, airport)

        folium.LayerControl(collapsed=False).add_to(self.map)
        return self

    def add_census_choropleth(self, *_args, **_kwargs) -> "CatchmentMap":
        """Add a Census choropleth (Phase 2 — stub)."""
        # TODO Phase 2: implement using folium.Choropleth on the joined table.
        raise NotImplementedError("Phase 2 — implement Census choropleth.")

    def add_transit_stops(self, *_args, **_kwargs) -> "CatchmentMap":
        """Add tube / rail / coach markers (Phase 2 — stub)."""
        raise NotImplementedError("Phase 2 — implement transit stop markers.")

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, filename: str = "london_competition_map.html") -> Path:
        out_dir = self.config.processed_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / filename
        self.map.save(str(path))
        self.log.info("Map saved to %s", path)
        return path

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _add_isochrone_layer(self, geojson_path: Path, airport: Airport) -> None:
        with geojson_path.open("r", encoding="utf-8") as f:
            geo_data = json.load(f)

        folium.GeoJson(
            geo_data,
            name=f"{airport.code} catchment area",
            style_function=lambda _feat, colour=airport.colour: {
                "fillColor": colour,
                "color": colour,
                "weight": self.config.map.line_weight,
                "fillOpacity": self.config.map.fill_opacity,
            },
        ).add_to(self.map)
        self.log.info("Added %s isochrones", airport.code)
