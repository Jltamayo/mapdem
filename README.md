# MAPDEM — prototype scaffold

Clean rebuild (previous scaffold discarded). Single, consolidated
architecture: **fully static, GitHub Pages, one linked-views app** — no
backend, no database. This replaces the earlier FastAPI/PostGIS draft;
that direction was dropped because a static site satisfies JUSTPLACE's
own hosting obligation (GitHub + DOI via OpenAIRE) directly, needs no
separately-funded hosting, and has fewer moving parts to fail before a
milestone deadline.

## What's real vs. placeholder right now

| Piece | Status |
|---|---|
| Repository structure | Real |
| Composite index method | Real algorithm (`analysis/composite_index.R`), run it yourself — this sandbox has no R to test it for you |
| NUTS2→NUTS3 duplication | Real algorithm (`analysis/nuts_disaggregation.R`), same caveat |
| Stata bridge | Real round-trip (pandas ⇄ `.dta` ⇄ R/haven) — tested here in Python |
| Eurostat fetcher | Real public API call — runnable today |
| Linked map + chart app (`docs/index.html`) | Real, visually verified (Playwright/Chromium, see `PROJECT_MEMORY.md` 2026-09-16): map renders, click-to-chart works, no console errors |
| NUTS3 geometries | **Real** — all 1345 EU NUTS3 regions, Eurostat GISCO 2024 boundaries (`data/NUTS_RG_20M_2024_4326.gpkg`, EPSG:4326), read via `pipeline/gpkg_reader.py` (no GDAL/geopandas dependency) |
| Indicator values | **Synthetic**, one row per real NUTS3 region: 5 domain indicators + 3 sub-indicators each (22 columns total) — swap `docs/data/processed/synthetic_indicators.csv` for partner data once it arrives; the region set and geometries don't need to change. Each domain's value is computed from its own 3 subs (not drawn independently), so the drill-down bars are internally consistent |
| Reference-average comparison (EU / country / NUTS1 / NUTS2 ticks on the chart) | Real feature, computed client-side in JS from the same indicator CSV (unweighted mean of sibling NUTS3 regions) — swapping in real indicator data recomputes it automatically, no script re-run needed |
| Domain tabs + choropleth map | Real feature: 5 navigable tabs (one per domain indicator), each recolouring the whole map (all 1345 regions) by that domain's value on a light→dark sequential scale (dark = always better, direction-corrected per domain) — gives a true "whole of Europe at a glance" view, not just per-region drill-down |

## Getting started in VS Code

### Python
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python pipeline/generate_synthetic_data.py   # creates docs/data/processed/*
python stata_bridge/read_dta_example.py      # proves the Stata round-trip
```

### R
```r
install.packages(c("dplyr", "tidyr", "readr", "haven", "tibble"))
source("analysis/composite_index.R")        # needs synthetic_indicators.csv first
source("analysis/nuts_disaggregation.R")    # self-contained toy example
```

### View the site locally
Open `docs/index.html` with a local server (e.g. VS Code's Live Server
extension) — not by double-clicking the file, since `fetch()` does not
work over `file://`.

## Publishing to GitHub Pages

1. Push this repository to GitHub.
2. Repo Settings → Pages → "Deploy from a branch" → branch `main`, folder
   `/docs`. No build step, no separate deploy workflow needed.
3. Tag a release at each milestone; the GitHub–Zenodo integration archives
   it and assigns a DOI via OpenAIRE.

## Why data lives under `docs/`

GitHub Pages only serves files inside the folder it's configured to
publish from. Since the site is published straight from `/docs`, every
file the app fetches (`docs/data/processed/*`) must live inside `docs/` —
there is no separate "internal" data folder for published layers. Only
`data/raw/` (untouched partner deliveries, never served publicly) sits
outside `docs/`.

## Where each piece comes from

- `pipeline/` — data ingestion / ETL (Python)
- `analysis/` — spatial statistics & typology methods (R)
- `stata_bridge/` — interoperability with partners running Stata
- `docs/` — the published site (app + data + methodology notes)
- `.github/workflows/ci.yml` — lint + smoke-test on every push

## Next steps (once real data starts arriving)

1. Agree the final indicator catalogue with POLIMI (Task 4.2) and PLUS
   (Task 3.3); update `docs/data/metadata/indicator_schema_example.json`.
2. Point `fetch_eurostat.py` at the confirmed dataset codes and replace
   `docs/data/processed/synthetic_indicators.csv` with real partner data,
   keyed by the same NUTS3 codes — the region set and geometries already
   cover all 1345 NUTS3 regions, so this is a drop-in swap, not a re-run of
   `generate_synthetic_data.py`.
3. Push to GitHub, enable Pages from `/docs`, connect Zenodo for DOI-tagged
   releases at each milestone.
