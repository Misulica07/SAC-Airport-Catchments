"""Public-transport ingestion (Phase 2 — skeleton).

Two upstream sources are wrapped behind one interface:

1. **TfL Open Data** — Journey Planner and station lookups, REST.
2. **Traveline GTFS** — national bus and coach feed, batched ZIP download.

In Phase 2, parsing GTFS feeds will most likely be delegated to
``gtfs-kit`` or ``partridge`` (already listed but commented in
``requirements.txt``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import TransitSettings
from src.ingestion.base import BaseIngester


class TfLIngester(BaseIngester):
    """Hit the TfL Unified API for routes, stations, and timetables."""

    api_key_env = "TFL_APP_KEY"  # Optional but increases rate limit.

    def __init__(self, output_dir: str | Path, settings: TransitSettings) -> None:
        super().__init__(output_dir=output_dir)
        self.settings = settings

    def fetch(self, from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> Any:  # type: ignore[override]
        """Return a TfL JourneyPlanner result for one origin-destination pair.

        TODO Phase 2 — implement against:
        GET ``{tfl_api_root}/Journey/JourneyResults/{from}/to/{to}``.
        """
        raise NotImplementedError("Phase 2 — wire up TfL Journey Planner.")

    def save(self, payload: Any, name: str) -> Path:  # type: ignore[override]
        path = self.output_dir / f"{name}.json"
        path.write_text(str(payload), encoding="utf-8")
        return path


class GTFSIngester(BaseIngester):
    """Download and unpack the Traveline GTFS national feed."""

    api_key_env = None

    def __init__(self, output_dir: str | Path, settings: TransitSettings) -> None:
        super().__init__(output_dir=output_dir)
        self.settings = settings

    def fetch(self, feed_name: str = "national") -> Path:  # type: ignore[override]
        """Download the GTFS ZIP for the given feed.

        TODO Phase 2 — stream the ZIP, validate it loads with ``gtfs-kit``,
        and return the path to the extracted directory.
        """
        raise NotImplementedError("Phase 2 — implement GTFS download.")

    def save(self, payload: Any, name: str) -> Path:  # type: ignore[override]
        # GTFS is already on disk after fetch(); save is a no-op stub.
        return Path(payload)
