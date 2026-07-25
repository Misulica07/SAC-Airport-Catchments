# SAC-Airport-Catchments
Interactive map for three UK airports 

# London Airport Catchment Areas — Interactive Journey Planner

**Students as Co-Creators | University of Westminster | 2025/2026**

A data-driven geospatial analysis of airport catchment areas for the three principal London airports: Heathrow (LHR), Gatwick (LGW) and Luton (LTN)

---

## Live Demo

**[Open the Interactive Journey Planner](https://misulica07.github.io/SAC-Airport-Catchments/airport_journey_planner_FINAL.html)**

> Requires a Google Maps API key — reach out to w2117157@westminster.ac.uk or mihaicatalin1707@gmail.com — paste it into the field at the top and click **Load Map**.

---

## Project Overview

This project was developed as part of the **Students as Co-Creators (SaC)** Disciplinary Research Collaboration programme at the University of Westminster, supervised by Dr Luis Delgado and Dr Michal Weiszer at the Centre for Air Traffic Management Research.

The research addresses three questions:
- How can open datasets be used to model surface access and egress mobility to airports?
- How can these models be used to analyse the criticality and resilience of surface access?
- How can competition between airports for overlapping catchment areas be assessed?

---

## Features

### Interactive Journey Planner
- **Click anywhere** on the map or select an ITL3 region to calculate real journey times to all three airports
- **Drive routing** with live traffic via Google Maps Directions API
- **Transit routing** via Google Maps (real timetables — train, tube, bus)
- **To Airport / From Airport** toggle
- **Straight-line distances** shown alongside routed times
- **ITL3 centroids** mapped to principal transport hubs (e.g. King's Cross, Victoria, Oxford station)

### Catchment Zone Analysis
- **Drive-time isochrones** at 30, 45 and 60 minutes per airport
- **Individual toggles** for each airport and time band
- **ITL3 population choropleth** — 50 regions, mid-2024 population estimates
- **Population and GDHI** shown on hover

### 24-Hour Journey Time Comparison
- Select up to **3 locations** and compare journey times across time slots
- Presets: Morning rush (08:15), Midday (12:30), Evening rush (17:00), Night (22:00), Custom
- **Drive times** powered by TomTom API with historical hourly traffic data
- **Transit times** powered by Google Maps with real timetables
- Results displayed as **3 separate tables**, one per airport

### Live Flight Information
- **Live FIDS** (Flight Information Display System) — arrivals and departures for all three airports
- Rolling window: last 1 hour to next 3 hours
- Powered by **AeroDataBox** via RapidAPI
- **Flight search** by flight number — shows route, status, delay, aircraft type
- **Animated flight path** — great circle route drawn on map with animated plane icon showing estimated position

---

## Repository Structure

```
SAC-Airport-Catchments/
│
├── airport_journey_planner_FINAL.html   # Final interactive map (GitHub Pages)
├── SAC_Pipeline.ipynb                   # Daniel's full pipeline notebook
├── SAC_AIRPORT_CATCHMENT_clean.ipynb    # Clean notebook for the journey planner
├── README.md                            # This file
│
└── data/                                # Raw data files
    ├── Transport.updated.xlsx           # Coach stops (NaPTAN)
    ├── Underground_Stations.csv         # London Underground stations
    ├── uk-railway-stations-main.zip     # National Rail stations
    ├── mye24tablesew.xlsx               # ONS mid-2024 population estimates
    └── regionalgrossdisposable...xlsx   # ONS GDHI 2023
```

---

## API Keys Required

| API | Purpose | Free Tier | Sign Up |
|-----|---------|-----------|---------|
| Google Maps JavaScript API | Map display, drive + transit routing | $200/month credit | [console.cloud.google.com](https://console.cloud.google.com) |
| TomTom Routing API | Hourly traffic-weighted drive times | 2,500 req/day | [developer.tomtom.com](https://developer.tomtom.com) |
| AeroDataBox (RapidAPI) | Live FIDS + flight search | 150 req/month | [rapidapi.com](https://rapidapi.com/aedbx-aedbx/api/aerodatabox) |
| OpenRouteService | Isochrone generation (pre-computed) | 500 req/day | [openrouteservice.org](https://openrouteservice.org) |

> **Security note:** Google Maps and TomTom keys are entered by the user in the browser and are never stored in this repository. AeroDataBox and TomTom keys are embedded in the HTML — restrict your keys to the GitHub Pages domain in the respective consoles.

---

## Getting Started

### Running the Journey Planner
1. Open the [live demo](https://misulica07.github.io/SAC-Airport-Catchments/airport_journey_planner_FINAL.html)
2. Paste your Google Maps API key into the field at the top
3. Click **Load Map**
4. Click anywhere on the map or select an ITL3 region from the dropdown

### Regenerating the HTML from Colab
1. Open `SAC_AIRPORT_CATCHMENT_clean.ipynb` in Google Colab
2. Add your ORS API key to the config cell
3. Run all cells in order
4. Download `airport_journey_planner_FINAL.html` from Google Drive
5. Upload to the repository to update GitHub Pages

---

## Key Findings

| Metric | LHR | LGW | LTN |
|--------|-----|-----|-----|
| Population within 30 min | 6,957,814 | 2,498,076 | 4,268,134 |
| Population within 60 min | 16,421,386 | 15,891,478 | 16,161,301 |
| Rail stations (60 min) | 471 | 376 | 246 |
| Tube stations (60 min) | 234 | 29 | 170 |

**Combined catchment (60 min):**
- 50 ITL3 regions · 21.1 million residents · £709 billion GDHI
- Three-way competition zone: **4,930 km²**

---

## Data Sources

| Dataset | Source |
|---------|--------|
| Drive-time isochrones | OpenRouteService v2 |
| ITL3 boundaries | ONS Geography (Jan 2021) |
| Population 2024 | ONS Mid-Year Estimates |
| GDHI 2023 | ONS Regional Accounts |
| Rail stations | NaPTAN / National Rail Open Data |
| Underground stops | TfL GIS Open Data |
| Coach stops | Traveline National Dataset |
| Live flight data | AeroDataBox via RapidAPI |
| Drive routing | Google Maps Directions API |
| Transit routing | Google Maps Directions API |
| Traffic-weighted drive times | TomTom Routing API |

---

## Team

**Student Partners**
- Daniel Hernández Gramajo
- Mihai-Cătălin Vasile

**Staff Partners**
- Dr Luis Delgado (Supervisor) — Centre for Air Traffic Management Research
- Dr Michal Weiszer (Co-Supervisor)

**Institution:** University of Westminster, School of Architecture and Cities

---

## Report

The full project report is available in the repository: `SaC_Final_Report_Airport_Catchments.docx`

---

*Students as Co-Creators Programme · University of Westminster · 2025/2026*
