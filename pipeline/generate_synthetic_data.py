"""
Generates synthetic indicator values for every NUTS3 region in the GISCO
GeoPackage (data/NUTS_RG_20M_2024_4326.gpkg), so the site (docs/index.html)
can be built and tested end-to-end against the full, real region set before
partner indicator data arrives. Only the indicator values are synthetic —
the geometries and region codes/names are real Eurostat GISCO 2024 data.
Partner data will simply replace this CSV later; the NUTS3 set and the
geometries stay the same.

Output goes straight into docs/data/processed/, because that folder is the
single source of truth GitHub Pages actually serves once the repo is
configured to publish from /docs (see README). There is no separate
"internal" copy — one location, always publishable.

Run:
    python pipeline/generate_synthetic_data.py
"""
import json
import random
from pathlib import Path

import pandas as pd

from gpkg_reader import read_features

random.seed(42)

GPKG_PATH = Path(__file__).resolve().parents[1] / "data" / "NUTS_RG_20M_2024_4326.gpkg"
GPKG_TABLE = "NUTS_RG_20M_2024_4326"

# Each of the 5 top-level indicators ("domains") is itself the combination of
# 3 base sub-indicators — matching JUSTPLACE's own domain descriptions (Task
# 4.1, docs/methodology.md / materials/Proposal-SEP-211195008.pdf p.154), not
# invented labels. Sub-indicator names are illustrative/synthetic (no such
# columns exist yet), but the *structure* — a domain built from several base
# indicators — is real and matches Task 4.1's own framing.
#
# NOTE on method: a domain's value is a simple mean of its sub-indicators,
# each oriented (inverted if needed) to the domain's own direction, skipping
# missing subs and only null if every sub is null. This is deliberately
# simpler than the rank-based method already candidate-implemented in
# analysis/composite_index.R (which treats these same 5 names as the *base*
# indicators of one overall composite, not as 5 domains each with their own
# subs) — the two are not reconciled yet; see PROJECT_MEMORY.md.
DOMAINS = {
    "objective_inequality_index": {
        "direction": "low_is_good",
        "short_label": "Objective inequality",
        "label": "Disparities in access to services, income & inequality",
        "subs": {
            "income_gap": ("low_is_good", "Income inequality (Gini-style gap)"),
            "access_to_services": ("high_is_good", "Access to healthcare/education/transport"),
            "poverty_risk_rate": ("low_is_good", "Share of population at risk of poverty"),
        },
    },
    "perceived_injustice": {
        "direction": "low_is_good",
        "short_label": "Perceived injustice",
        "label": "Perceived economic injustice & well-being",
        "subs": {
            "perceived_unfairness": ("low_is_good", "Share reporting unfair treatment (ESS-style)"),
            "life_satisfaction": ("high_is_good", "Self-reported life satisfaction"),
            "economic_optimism": ("high_is_good", "Optimism about future economic conditions"),
        },
    },
    "civic_participation": {
        "direction": "high_is_good",
        "short_label": "Civic participation",
        "label": "Voting behaviour & civic participation",
        "subs": {
            "voter_turnout": ("high_is_good", "Voter turnout in the most recent elections"),
            "protest_activity": ("high_is_good", "Participation in protests/demonstrations"),
            "associational_membership": ("high_is_good", "Membership in civic/associational orgs"),
        },
    },
    "democratic_trust": {
        "direction": "high_is_good",
        "short_label": "Democratic trust",
        "label": "Trust & democratic resilience",
        "subs": {
            "institutional_trust": ("high_is_good", "Trust in national/local institutions"),
            "political_efficacy": ("high_is_good", "Sense that one's political voice matters"),
            "corruption_perception": ("low_is_good", "Perceived level of corruption"),
        },
    },
    "media_access_index": {
        "direction": "high_is_good",
        "short_label": "Media access",
        "label": "News deserts / media access",
        "subs": {
            "local_media_presence": ("high_is_good", "Presence of local news outlets"),
            "digital_literacy": ("high_is_good", "Digital literacy / media literacy"),
            "internet_coverage": ("high_is_good", "Broadband/internet coverage"),
        },
    },
}

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "data" / "processed"


def load_all_nuts3_regions(gpkg_path=GPKG_PATH, table=GPKG_TABLE):
    """Every NUTS3 region in the GISCO GeoPackage, as (properties, geometry)
    pairs — read once and reused for both the indicator table and the
    GeoJSON, so the ~1345 geometries aren't decoded twice."""
    return read_features(gpkg_path, table, ["NUTS_ID", "NAME_LATN"], where_sql="LEVL_CODE = 3")


def make_indicator_table(regions):
    """One row per real NUTS3 region: the 3 sub-indicators of each domain
    (each independently ~20% missing, simulating "highly inhomogeneous"
    real-world missingness) plus the domain's own value, computed from
    those subs — not drawn independently. NUTS2 parent is derived from the
    code's standard Eurostat nesting (NUTS3 code's first 4 characters)."""
    rows = []
    for props, _geometry in regions:
        nuts3 = props["NUTS_ID"]
        row = {"nuts2": nuts3[:4], "nuts3": nuts3}
        for domain_key, domain in DOMAINS.items():
            sub_values = {}
            for sub_key in domain["subs"]:
                is_missing = random.random() <= 0.2
                sub_values[sub_key] = None if is_missing else round(random.uniform(0, 100), 1)

            oriented = [
                v if sub_direction == domain["direction"] else (100 - v)
                for sub_key, (sub_direction, _desc) in domain["subs"].items()
                if (v := sub_values[sub_key]) is not None
            ]
            row[domain_key] = round(sum(oriented) / len(oriented), 1) if oriented else None
            row.update(sub_values)
        rows.append(row)
    return pd.DataFrame(rows)


def load_all_nuts_names(gpkg_path=GPKG_PATH, table=GPKG_TABLE):
    """Real region names (NAME_LATN — each region's own local-language Latin-
    script name, e.g. "Deutschland", "Cataluña") for every NUTS level in the
    GeoPackage (0=country, 1, 2, 3), keyed by code. This is static reference
    data independent of indicator values — generated once from GISCO, it
    doesn't need to change when indicators are swapped for real partner
    data."""
    rows = read_features(gpkg_path, table, ["NUTS_ID", "NAME_LATN"])
    # A few GISCO rows (e.g. North Macedonia) carry stray leading/trailing
    # whitespace in NAME_LATN itself — strip it rather than pass it through.
    return {props["NUTS_ID"]: props["NAME_LATN"].strip() for props, _geometry in rows}


def build_domain_hierarchy():
    """The DOMAINS structure (labels, directions, sub-indicators) as plain
    JSON, so docs/index.html reads the tab/drill-down hierarchy from one
    file instead of a second hand-kept copy in JS that could drift from
    this one."""
    return {
        domain_key: {
            "direction": domain["direction"],
            "short_label": domain["short_label"],
            "label": domain["label"],
            "subs": {
                sub_key: {"direction": sub_direction, "label": sub_label}
                for sub_key, (sub_direction, sub_label) in domain["subs"].items()
            },
        }
        for domain_key, domain in DOMAINS.items()
    }


def build_geojson(regions):
    """FeatureCollection from the same (properties, geometry) pairs used for
    the indicator table, so every indicator row has a matching boundary and
    vice versa."""
    features = [
        {
            "type": "Feature",
            "properties": {"nuts3": props["NUTS_ID"], "name": props["NAME_LATN"]},
            "geometry": geometry,
        }
        for props, geometry in regions
    ]
    return {"type": "FeatureCollection", "features": features}


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    regions = load_all_nuts3_regions()

    df = make_indicator_table(regions)
    indicators_path = OUT_DIR / "synthetic_indicators.csv"
    df.to_csv(indicators_path, index=False)
    print(f"Wrote {indicators_path} ({len(df)} rows)")

    geo = build_geojson(regions)
    geo_path = OUT_DIR / "synthetic_regions.geojson"
    with open(geo_path, "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=2, ensure_ascii=False)
    print(f"Wrote {geo_path} ({len(geo['features'])} features, real NUTS3 boundaries)")

    names = load_all_nuts_names()
    names_path = OUT_DIR / "nuts_names.json"
    with open(names_path, "w", encoding="utf-8") as f:
        json.dump(names, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"Wrote {names_path} ({len(names)} region names, all NUTS levels 0-3)")

    hierarchy = build_domain_hierarchy()
    hierarchy_path = OUT_DIR / "domain_hierarchy.json"
    with open(hierarchy_path, "w", encoding="utf-8") as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
    print(f"Wrote {hierarchy_path} ({len(hierarchy)} domains)")
