# Contributing to MAPDEM (prototype stage)

This repository runs entirely on **synthetic data** so the pipeline and site
can be built and tested before partner data (POLIMI, PLUS, RUG, EMN) arrives.

## If you work in R or Stata and are not comfortable with Python/Git

You do not need to touch `pipeline/`. You can contribute by:
- Dropping a `.dta` or `.csv` file into `data/raw/` and opening a GitHub
  issue describing what it contains.
- Editing the R scripts in `analysis/` directly — no Python dependency.

## Branching

- `main`: always publishable (GitHub Pages serves it live), protected.
- `develop`: integration branch.
- `feature/<short-description>`: your working branch, merged via pull
  request into `develop`.

## Before opening a pull request

- Python: `flake8 pipeline stata_bridge`
- R: `Rscript -e 'lintr::lint_dir("analysis")'`
- If you changed the indicator schema, update
  `docs/data/metadata/indicator_schema_example.json` accordingly.

## A note on what lives where

- `data/raw/` — untouched partner deliveries, never published.
- `docs/data/processed/` — the exact files the live site reads. GitHub
  Pages can only serve files inside `docs/`, so anything the map or chart
  needs must end up here, not in a separate top-level `data/processed/`.
