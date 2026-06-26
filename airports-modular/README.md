# Westminster Airport Catchment

[![Tests](https://img.shields.io/badge/tests-pytest-blue)]() [![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()

Data-engineering pipeline that characterises the **overlapping catchment areas**
of the London Multi-Airport System — **Luton (LTN)**, **Heathrow (LHR)** and
**Gatwick (LGW)** — combining drive-time isochrones with demographic and
public-transport accessibility data.

Developed under the *Students as Co-Creator* programme at the University of
Westminster, supervised by **Luis Delgado** and **Michal Weiszer**.

---

## 1. What this project does

| Phase | Stage | Output | Status |
|-------|-------|--------|--------|
| **1** | Driving isochrones (30 / 45 / 60 min) via OpenRouteService | `data/raw/{CODE}_isochrones.geojson` | ✅ |
| **1** | Interactive multi-airport competition map | `data/processed/london_competition_map.html` | ✅ |
| **2** | UK Census spatial join (LSOA, population, IMD) | `data/processed/catchment_demographics.parquet` | 🟡 skeleton |
| **2** | Multimodal accessibility (TfL + GTFS) | `data/processed/multimodal_isochrones.geojson` | 🟡 skeleton |
| **3** | EU comparison (EUROSTAT) | TBD | ⏳ |

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the design rationale.

---

## 2. Repository layout

```
westminster-airport-catchment/
├── config/
│   └── airports.yaml          ← all parameters live here (airports, CRS, thresholds…)
├── data/
│   ├── raw/                   ← outputs of the ingestion layer (git-ignored)
│   ├── interim/               ← cleaned intermediates (git-ignored)
│   └── processed/             ← final tables and HTML maps (git-ignored)
├── docs/
│   └── ARCHITECTURE.md
├── src/
│   ├── config.py              ← typed YAML + .env loader
│   ├── pipeline.py            ← end-to-end orchestrator (CLI entry point)
│   ├── ingestion/
│   │   ├── base.py            ← shared retry / auth / logging
│   │   ├── isochrones.py      ← OpenRouteService client (Phase 1)
│   │   ├── census.py          ← UK Census / Nomis client (Phase 2 — skeleton)
│   │   └── transit.py         ← TfL + GTFS clients (Phase 2 — skeleton)
│   ├── analysis/
│   │   └── spatial_join.py    ← isochrone × geography overlay + area weighting
│   ├── visualization/
│   │   └── maps.py            ← composable folium map
│   └── utils/
│       ├── geo.py             ← CRS helpers and area-weighted aggregation
│       └── logging.py         ← single root logger
├── tests/                     ← pytest unit tests
├── .env.example               ← template for required API keys
├── .gitignore
├── pyproject.toml             ← packaging + ruff + pytest config
├── requirements.txt
└── README.md
```

---

## 3. Quick start

### 3.1 Install

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3.2 Configure secrets

```bash
cp .env.example .env
# then open .env and paste your OpenRouteService key
```

You can get a free OpenRouteService key at
<https://openrouteservice.org/dev/#/signup>.

### 3.3 Run the pipeline

```bash
python -m src.pipeline                       # full run
python -m src.pipeline --skip-isochrones     # reuse cached GeoJSON
```

Open `data/processed/london_competition_map.html` in any browser to
inspect the map.

### 3.4 Run the tests

```bash
pytest
```

---

## 4. Adding a new airport

Append an entry to `config/airports.yaml`:

```yaml
airports:
  - code: "STN"
    name: "London Stansted"
    lon: 0.235000
    lat: 51.885000
    colour: "orange"
```

No code change required. The next pipeline run will fetch the isochrones,
add a new map layer with the chosen colour, and join Stansted into the
analytical outputs in Phase 2.

---

## 5. Roadmap

The Phase 2 architecture is already in place — `ingestion/census.py`,
`ingestion/transit.py` and `analysis/spatial_join.py` expose the final
function signatures behind `NotImplementedError` markers. Filling them in
does not require any structural change to the pipeline.

| Step | Module | Phase |
|------|--------|-------|
| Implement `CensusIngester.fetch_boundaries` against the ONS Geography Portal | `ingestion/census.py` | 2 |
| Implement `CensusIngester.fetch_table` against the Nomis API | `ingestion/census.py` | 2 |
| Wire `analysis/spatial_join.overlay_isochrones_with_geography` into `pipeline.stage_census` | `pipeline.py` | 2 |
| Implement `TfLIngester.fetch` against the TfL Journey Planner | `ingestion/transit.py` | 2 |
| Implement `GTFSIngester.fetch` against Traveline | `ingestion/transit.py` | 2 |
| Add an EUROSTAT comparison module | `ingestion/eurostat.py` | 3 |

---

## 6. Team

| Role | Person |
|------|--------|
| Supervisor | Luis Delgado |
| Co-supervisor | Michal Weiszer |
| Student researcher | Daniel Hernández Gramajo |
| Student researcher (sister repo) | Mihai-Cătălin Vasile |
| Institution | University of Westminster (Marylebone campus) |

---

## 7. Licence

For academic use within the Students as Co-Creator programme at the
University of Westminster. Contact the project team for any reuse outside
that context.
