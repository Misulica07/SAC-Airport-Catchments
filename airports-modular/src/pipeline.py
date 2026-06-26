"""End-to-end pipeline orchestrator.

This is the only module that knows the order of operations. Each step is a
thin wrapper around a single ingester or analysis function, so the file
remains short and human-readable. To add a new step (e.g. Census in
Phase 2), append it here and the rest of the codebase stays untouched.

Usage
-----
From the project root::

    python -m src.pipeline                       # default config
    python -m src.pipeline --config config/airports.yaml
    python -m src.pipeline --skip-isochrones    # reuse cached GeoJSON
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import Config, load_config
from src.ingestion import IsochroneIngester
from src.utils.logging import configure_logging, get_logger
from src.visualization import CatchmentMap

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------


def stage_isochrones(config: Config) -> None:
    """Stage 1 — pull driving isochrones for every airport in the config."""
    ingester = IsochroneIngester(
        output_dir=config.raw_dir,
        settings=config.isochrones,
    )
    for airport in config.airports:
        payload = ingester.fetch(airport)
        ingester.save(payload, airport.code)


def stage_map(config: Config) -> Path:
    """Stage 2 — render the multi-airport HTML map from the cached GeoJSON."""
    return (
        CatchmentMap(config)
        .add_isochrones()
        .save(filename="london_competition_map.html")
    )


def stage_census(_config: Config) -> None:
    """Stage 3 — Census ingestion + spatial join. TODO Phase 2."""
    log.info("Stage 3 (Census) is a Phase 2 placeholder — skipping for now.")


def stage_transit(_config: Config) -> None:
    """Stage 4 — TfL / GTFS ingestion + multimodal accessibility. TODO Phase 2."""
    log.info("Stage 4 (Transit) is a Phase 2 placeholder — skipping for now.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the airport-catchment pipeline.")
    parser.add_argument(
        "--config",
        default="config/airports.yaml",
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--skip-isochrones",
        action="store_true",
        help="Reuse GeoJSON already present under data/raw/ (saves API quota).",
    )
    args = parser.parse_args(argv)

    configure_logging()
    config = load_config(args.config)

    log.info("Starting pipeline with %d airports", len(config.airports))

    if not args.skip_isochrones:
        stage_isochrones(config)
    else:
        log.info("Skipping isochrone download (--skip-isochrones).")

    stage_map(config)
    stage_census(config)
    stage_transit(config)

    log.info("Pipeline finished.")


if __name__ == "__main__":
    main()
