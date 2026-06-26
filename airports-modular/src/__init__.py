"""Westminster Airport Catchment — analytical package.

Submodules:
    config         — typed configuration loaded from YAML + .env.
    ingestion      — data acquisition (ORS isochrones, UK Census, transit).
    analysis       — spatial joins and catchment aggregations.
    visualization  — folium maps and matplotlib summaries.
    utils          — cross-cutting helpers (geo, logging).
    pipeline       — orchestrator that wires the full run.
"""

__version__ = "0.2.0"
