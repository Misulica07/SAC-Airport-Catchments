# Architecture

This document describes the structure of the codebase and the rationale
behind each design decision. The goal is that anyone — including a new
team member or a reviewer — can read this file and predict where any given
piece of logic lives, and why.

---

## 1. Layered architecture

The project follows a strict three-layer separation:

```
┌───────────────────────────────────────────────────────────────┐
│  pipeline.py                                                  │  ← Orchestration
├───────────────────────────────────────────────────────────────┤
│  ingestion/      analysis/      visualization/                │  ← Domain layers
├───────────────────────────────────────────────────────────────┤
│  config/         utils/         data/                         │  ← Cross-cutting
└───────────────────────────────────────────────────────────────┘
```

- **`ingestion/`** — fetches data from upstream sources (OpenRouteService,
  ONS, TfL). Writes raw payloads to `data/raw/`. **Never** transforms.
- **`analysis/`** — consumes `data/raw/` and emits cleaned tables to
  `data/interim/` or `data/processed/`. **Never** calls the network.
- **`visualization/`** — turns processed tables into folium maps or static
  charts. **Never** writes back into `data/raw/`.

The benefits:

1. A failure in one layer (e.g. ORS rate-limited) does not corrupt the
   layer below it.
2. The analysis layer is testable without API keys.
3. Adding a new source (Census, GTFS) only requires a new ingester; the
   analytical code remains unchanged.

---

## 2. Configuration as data

All static parameters live in `config/airports.yaml`. The code never holds
magic numbers; it asks the `Config` dataclass instead. Adding a new
airport, changing a CRS, or switching the deprivation table is a YAML
edit, not a code change.

The loader (`src/config.py`) is **typed**. Every value is exposed as a
strongly typed attribute, so an IDE autocompletes `cfg.isochrones.profile`
rather than `cfg["isochrones"]["profile"]`. Misspellings fail at load
time, not three function calls deep.

---

## 3. Secrets

API keys live in a git-ignored `.env`. The base ingester reads them via
`os.environ` and raises a clear error if they are missing. The
`.env.example` template documents every variable so a new contributor
knows what to set without reading the source code.

The previous version held the key as a hard-coded string in `main.py`.
That key has been revoked; the new code can never repeat that mistake
because there is no place for a literal to live.

---

## 4. The base ingester

All ingesters inherit from `BaseIngester`, which provides:

- `_read_api_key()` — environment-driven, fails fast.
- `_post_with_retry()` — exponential backoff for transient HTTP errors.
- A subclass-bound `logger`.
- Forced `output_dir` creation.

Subclasses only have to implement `fetch()` and `save()`. This pattern
makes adding the Census and GTFS ingesters in Phase 2 mechanical.

---

## 5. CRS discipline

The codebase has two CRSs:

| Use case                                  | CRS                        |
|-------------------------------------------|----------------------------|
| Folium rendering, ORS responses            | `EPSG:4326` (WGS-84)       |
| Distance / area math, spatial joins        | `EPSG:27700` (BNG)         |

`src/utils/geo.py` provides `to_projected()` / `to_geographic()` so no
caller computes distances in degrees by accident. Every spatial join in
the analysis layer reprojects first.

---

## 6. Area-weighted aggregation

When an LSOA straddles the boundary of an isochrone, naive intersection
counts the population twice. The analytical layer attaches an
`area_weight` column to every overlay row, defined as

```
area_weight = area_intersected / area_total_of_LSOA
```

and multiplies extensive variables (population, dwellings) by that
weight before summing. The unit test `test_area_weight_handles_half_overlap`
pins this contract.

---

## 7. Pipeline orchestration

`src/pipeline.py` is the only place that knows the run order. Each
stage is a 5-to-10-line wrapper around one ingester or analysis call.
The CLI takes `--skip-isochrones` to reuse cached GeoJSON, which saves
ORS quota while iterating on the visualisation or analysis code.

---

## 8. Testing strategy

- **Unit tests** for pure functions (`area_weight`, CRS round-trips,
  config loading). Run in CI with no network.
- **Integration tests** (TODO) will live alongside Phase 2: spin up a
  fixture Census table + isochrone, run the full overlay, assert the
  aggregate population matches a known answer.
- **Smoke run** is just `python -m src.pipeline --skip-isochrones` — if
  that produces a non-empty HTML map, the wiring is intact.

---

## 9. Roadmap

| Stage                                 | Status              | Owner          |
|---------------------------------------|---------------------|----------------|
| 1. ORS isochrones                     | ✅ in `isochrones.py` | Daniel        |
| 2. HTML map (folium)                  | ✅ in `maps.py`       | Daniel        |
| 3. UK Census ingestion (Nomis + ONS)  | 🟡 skeleton          | Daniel — Phase 2 |
| 4. Spatial join + area weighting      | ✅ utilities ready    | Daniel — Phase 2 |
| 5. TfL / GTFS ingestion               | 🟡 skeleton          | Daniel — Phase 2 |
| 6. Multimodal isochrones (r5py)       | ⏳ not started        | TBD            |
| 7. EU comparison (EUROSTAT)           | ⏳ not started        | TBD            |
