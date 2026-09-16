# CLAUDE.md — MAPDEM

MAPDEM (Mapping Democracy) is D4.2 of the JUSTPLACE Horizon Europe project (WP4/Task 4.1, led by
UB) — an interactive territorial atlas translating multilevel democracy/inequality data into
public visualisations. This repo is the technical scaffold for that deliverable.

## Project context (verified against the real proposal, 2026-09-16)

`materials/Proposal-SEP-211195008.pdf` is the actual submitted JUSTPLACE proposal (Part B, 164
pages, Proposal ID 101286505, call HORIZON-CL2-2025-01-DEMOCRACY-08, HORIZON-RIA, Lump Sum grant)
— moved here from `docs/` on 2026-09-16 (see "Known open flags" below, item 3) because `docs/` is
what GitHub Pages would publish, and this PDF carries per-partner budgets and researchers'
emails/ORCID IDs. This is the only proposal source document that verifiably exists in this
repository (see item 2 below). Facts below are cited to it directly; use it, not
`PROJECT_PROTOCOL.md`'s citations to the `.docx` files described in item 2, when you need to
re-check something.

- WP4 "Measuring inequality – democracy nexus" is led by **POLIMI**; **UB leads Task 4.1**
  "Spatial trends of inequalities and democratic attitudes" (M6–M18) and also leads WP3 (PDF p.151,
  p.154). Task 4.1's twofold aim: (1) new indicators of objective+subjective territorial
  disparities (income/services access, perceived injustice, trust, civic/voting behaviour, media
  accessibility); (2) build MAPDEM to visualise those indicators plus the regional typologies from
  Task 4.2 (POLIMI-led, M12–M24). Both converge into D4.1 (multi-level database) and D4.2 (MAPDEM),
  both due M18, both PU (public) (PDF p.154, p.162).
- Milestone M5 "MAPDEM published" (WP4, due month 18): "Interactive atlas available online and
  functional" (PDF p.162).
- UB team (PDF p.80): Vicente Royuela (PI), Oscar Claveria González, Rosina Moreno Serrano, Ernest
  Miguelez Sanchez, Raul Ramos Lobo, David Castells-Quintana (his listed email is `@uab.cat`, not
  `@ub.edu` — flag if citing his affiliation formally). UB budget: €341,250 of the consortium's
  €3,493,125 total (PDF p.108). UB's 48 person-months split: WP1 1.5 / WP2 1.0 / WP3 9.5 / WP4 23.0
  / WP5 7.5 / WP6 3.5 / WP7 0 / WP8 2.0 (PDF p.163).
- Data management commitments (PDF p.134, not yet implemented in this repo): FAIR
  principles, DMP due M6 (D1.2), OpenAIRE as default repository, INSPIRE-compliant geospatial
  sharing (Copernicus, OpenStreetMap), GitHub with DOI via OpenAIRE for code/models, metadata in
  Dublin Core + ISO 19115.
- Democracy Studios pilot territories: **7**, per the user (2026-09-16, confirmed directly,
  overriding an earlier note here) — use 7 as the working figure. Task 5.1's text in the proposal
  PDF (p.155) names only six explicitly (Iasi RO, Flanders BE, Karditsa & Volos EL, Hauts-de-France
  FR, Barcelona ES, Bratislava SK); the 7th isn't named in that passage. Don't re-flag this as a
  discrepancy — it's settled at 7.

## Before doing anything in this project

1. Read `.claude/PROJECT_PROTOCOL.md` — resolved, project-specific parameter values (tech stack,
   deployment, language, editorial style, data-integrity rules). Check there before asking the
   user something already decided; add a new row there instead of re-deciding per session.
2. Read `.claude/PROJECT_MEMORY.md` — append-only log of past work sessions and decisions on this
   project. Skim recent entries for context before starting new work.
3. Verify claims in those files against the actual repository state before relying on them — see
   "Known open flags" below for live examples of these files disagreeing with the repo.

## Repository layout (observed 2026-09-16)

- `pipeline/` — Python ETL (`fetch_eurostat.py`, `generate_synthetic_data.py`, `gpkg_reader.py` —
  a dependency-free GeoPackage reader, no GDAL/geopandas/fiona)
- `analysis/` — R spatial statistics/typology (`composite_index.R`, `nuts_disaggregation.R`)
- `stata_bridge/` — Stata interoperability round-trip (Python + R versions)
- `docs/` — the published site (`index.html`, `data/`, `methodology.md`); GitHub Pages serves
  straight from this folder, so anything the app fetches must live under `docs/data/`. Keep
  non-public material (proposal/admin documents, anything with budgets or personal data) out of
  this folder — see `materials/` below.
- `materials/` — non-public project/admin documents not meant for GitHub Pages, e.g.
  `Proposal-SEP-211195008.pdf` (moved out of `docs/` on 2026-09-16 for exactly this reason).
- `data/` — NUTS geometries: `NUTS_RG_10M_2024_4326.gpkg` (real GISCO 2024, EPSG:4326 — the one the
  pipeline actually uses for the main map, since 2026-09-16) and `outermost_regions_01M_4326.geojson`
  (higher-resolution GISCO 1M boundaries for just the 14 outermost-region NUTS3 codes, since those
  are rendered zoomed in tight); plus partner deliveries not served publicly (`data/raw/`)
- `.claude/PROJECT_PROTOCOL.md` — resolved project-specific parameters
- `.claude/PROJECT_MEMORY.md` — append-only history of work sessions
- `.claude/skills/` — academic-manuscript skill suite (see `.claude/skills/README.md` for how it
  uses the two files above)

## Keeping project memory active

`.claude/PROJECT_MEMORY.md` only has value if every session that resolves something non-trivial
adds to it. Rule (defined generically in `.claude/skills/README.md`, applies to this file in
general, not only to the six manuscript skills):

- At the end of a work session that makes a decision, resolves an ambiguity, finds a discrepancy,
  or completes a meaningful piece of work — append an entry. Never rewrite or reorder previous
  entries; this is append-only.
- Entry format:

  ```markdown
  ## <ISO date> — <short label for the session/skill>

  - **Papers/documentos afectados**: <list or "N/A">
  - **Decisiones tomadas**: <decisions, especially ones needing user confirmation>
  - **Hallazgos/observaciones**: <what was discovered — defects, gaps, discrepancies>
  - **Estado resultante**: <what's done, what's left open>
  ```

- If a parameter this project needs isn't in `PROJECT_PROTOCOL.md` yet, decide it once with the
  user, add a row there, and reuse it rather than re-deciding it per document.

## Known open flags

1. **Unresolved as of 2026-09-16.** `PROJECT_PROTOCOL.md` states the pipeline is now **R-only**
   and that the Python/FastAPI legacy code was deleted on 2026-09-15. The repository as it
   actually exists still has a working Python side (`pipeline/`, `stata_bridge/read_dta_example.py`,
   `requirements.txt` pinning pandas/requests/eurostat), and both `README.md` and `CONTRIBUTING.md`
   describe a Python+R hybrid pipeline, not an R-only one. Confirm with the user which is current
   before assuming either version.
2. **Clarified by the user 2026-09-16, not an integrity problem.** `PROJECT_PROTOCOL.md` cites
   `docs/MATERIAL/MAPDEM_Work_Proposal_UB.docx`,
   `docs/MATERIAL/MAPDEM_UB_Team_Proposal_GrantAgreement.docx` and
   `docs/MATERIAL/MAPDEM_Technology_Report.docx` throughout, and `docs/MATERIAL/` doesn't exist in
   this repository. The user confirmed these were early pilot/draft files used to decide on an
   approach, not currently relevant, and will be supplied again if/when actually needed — don't
   chase this as a lost-file problem. `materials/Proposal-SEP-211195008.pdf` (see "Project
   context" above) is the one real proposal source currently in the repo; treat any
   `PROJECT_PROTOCOL.md` row whose only citation is one of those three `.docx` files as unverified
   until the user supplies them.
3. **Resolved 2026-09-16.** The proposal PDF used to sit in `docs/` (GitHub-Pages-published
   folder) alongside per-partner budgets and researchers' emails/ORCID IDs. Moved to
   `materials/Proposal-SEP-211195008.pdf` at the user's request — keep any future admin/non-public
   documents there too, not under `docs/`.

## Language and editorial style

- Global writing rules (British English spelling, punctuation, the `Note:` label convention, no
  invented figures) come from the user's global `CLAUDE.md` and apply here too — not repeated in
  this file to avoid drift between the two.
- Working language for MAPDEM deliverables: English by default (JUSTPLACE is an international
  consortium). Catalan/Spanish only if the user explicitly asks for a specific internal
  deliverable.

## Data integrity

- Indicator values currently in this repo (`docs/data/processed/synthetic_indicators.csv`, one row
  per real NUTS3 region) are synthetic placeholders, not real observations — never present them as
  empirical results.
- NUTS3 boundaries ARE real (Eurostat GISCO 2024, `data/NUTS_RG_10M_2024_4326.gpkg`, all 1345
  regions) — this is not placeholder data, only the indicator values are.
