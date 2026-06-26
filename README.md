# SAC-Airport-Catchments
Interactive map for three UK airports 
## Summary
Adds a modular, configurable architecture next to the existing Colab
script, designed to host the Phase 2 work (UK Census + TfL/GTFS)
agreed with Luis on 2026-04-15.

## Layout
- `sac_airport_catchment_main.py` (existing) — kept intact.
- `airports-modular/` (new) — modular pipeline:
  - `src/ingestion/` — typed clients with retry & env-var auth.
  - `src/analysis/` — spatial-join and area-weighted aggregation.
  - `src/visualization/` — composable folium maps.
  - `docs/ARCHITECTURE.md` — design rationale.

## Why
- Phase 2 introduces two new data sources (Census, TfL/GTFS) plus a
  spatial-join layer. Adding them to the monolithic script would push
  past 4 000 lines.
- The ORS API key is now read from `.env` instead of being hard-coded.
- Tests run with no network and pin the area-weighting contract.

## Phase 2 hooks
- `airports-modular/src/ingestion/census.py` — Nomis + ONS Geography skeleton.
- `airports-modular/src/ingestion/transit.py` — TfL + GTFS skeletons.
- `airports-modular/src/analysis/spatial_join.py` — overlay + area-weighting helpers ready.

## Not in this PR
- Merging the existing analytical work (ITL3 join, GDHI, transport
  stops, journey planner) into the modular layout. That belongs in a
  follow-up branch and should be discussed with the team.

## Test plan
- [x] `pytest` passes locally (8/8 tests).
- [x] `python -m src.pipeline` produces a non-empty
      `airports-modular/data/processed/london_competition_map.html`.
- [x] `python -m src.pipeline --skip-isochrones` works against cached
      GeoJSON.
