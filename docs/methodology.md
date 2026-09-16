# Methodology notes

- **Composite index (rank-based, missing-data tolerant)** — implemented in
  `analysis/composite_index.R` (`build_domain_index()`): rank each region per
  indicator (reversed for undesirable indicators), normalise by the number
  of regions with valid data, average within a domain, then across domains.
  Chosen because it only needs one valid indicator per region/domain,
  tolerating uneven, non-random missingness across 27+ countries.

- **NUTS2→NUTS3 disaggregation by duplication** — implemented in
  `analysis/nuts_disaggregation.R` (`disaggregate_nuts2_to_nuts3()`), with
  an `is_duplicated` flag per indicator so the map can visually distinguish
  duplicated (NUTS2-derived) values from genuinely observed NUTS3 values.

- **Five data layers** — reflected in the `INDICATORS` dict in
  `pipeline/generate_synthetic_data.py` (one synthetic proxy per layer;
  extend as the real catalogue is agreed with POLIMI/Task 4.2 and
  PLUS/Task 3.3).

Source for the two borrowed methods above: PREMIUM_EU, *Atlas of Regional
Development*, KNAW et al. (2025), Zenodo, DOI: 10.5281/zenodo.15754498,
CC BY 4.0.

## Real NUTS geometry (replacing the placeholder squares)

`pipeline/generate_synthetic_data.py` currently generates fake square
polygons. Real NUTS boundaries are public and free from Eurostat's GISCO
service, already in EPSG:4326 (no reprojection needed for a web map). Swap
the placeholder geometry generator for a GISCO download + filter step when
ready — the rest of the pipeline (indicator join, composite index,
disaggregation) does not need to change.
