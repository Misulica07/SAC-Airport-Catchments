"""Driving-isochrone extraction via OpenRouteService.

Migrated from the original ``data_ingestion.OpenRouteServiceAPI`` class. The
behaviour is identical from the API's point of view, but:

* The API key is read from the environment via :class:`BaseIngester`,
  not hard-coded.
* Retries with exponential backoff are inherited from the base class.
* GeoJSON is written using a dedicated I/O helper.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import Airport, IsochroneSettings
from src.ingestion.base import BaseIngester


class IsochroneIngester(BaseIngester):
    """Pull isochrone polygons from OpenRouteService for a single airport."""

    api_key_env = "ORS_API_KEY"
    base_url = "https://api.openrouteservice.org/v2/isochrones"

    def __init__(
        self,
        output_dir: str | Path,
        settings: IsochroneSettings,
    ) -> None:
        super().__init__(
            output_dir=output_dir,
            retry_attempts=settings.retry_attempts,
            retry_backoff_seconds=settings.retry_backoff_seconds,
            timeout_seconds=settings.request_timeout_seconds,
        )
        self.settings = settings

    # ------------------------------------------------------------------
    # BaseIngester implementation
    # ------------------------------------------------------------------

    def fetch(self, airport: Airport) -> dict[str, Any]:  # type: ignore[override]
        """Return the raw GeoJSON FeatureCollection for one airport."""
        endpoint = f"{self.base_url}/{self.settings.profile}"
        headers = {
            "Accept": "application/json, application/geo+json",
            "Authorization": self.api_key or "",
            "Content-Type": "application/json; charset=utf-8",
        }
        body = {
            "locations": [[airport.lon, airport.lat]],
            "range": self.settings.thresholds_seconds,
            "range_type": "time",
            "smoothing": self.settings.smoothing,
        }
        self.log.info("Requesting isochrones for %s (%s)", airport.code, airport.name)
        payload = self._post_with_retry(endpoint, json=body, headers=headers)
        self._stamp_features_with_airport(payload, airport)
        return payload

    def save(self, payload: dict[str, Any], name: str) -> Path:  # type: ignore[override]
        path = self.output_dir / f"{name}_isochrones.geojson"
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.log.info("Saved %s", path.relative_to(path.parents[2]))
        return path

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _stamp_features_with_airport(payload: dict[str, Any], airport: Airport) -> None:
        """Add airport metadata into every feature so downstream joins are easy."""
        for feature in payload.get("features", []):
            feature.setdefault("properties", {}).update(
                {
                    "airport_code": airport.code,
                    "airport_name": airport.name,
                }
            )
