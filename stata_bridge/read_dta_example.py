"""
Stata <-> Python bridge: .dta is treated strictly as an INPUT format from
partners who run causal models in Stata (e.g. Task 4.2 outputs); everything
downstream uses CSV as the canonical, publishable format.

This script writes a tiny synthetic .dta (no Stata licence needed — pandas
can both read and write Stata files) purely so the round-trip is testable
before a real partner file arrives.

Run:
    python stata_bridge/read_dta_example.py
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "docs" / "data" / "processed"


def make_fake_partner_dta():
    """Stand-in for a Task 4.2 (POLIMI) or Task 5.1 regression output delivered as .dta."""
    df = pd.DataFrame({
        "nuts3": ["ES511", "ES512", "ES513"],
        "coef_inequality_on_trust": [-0.42, -0.31, -0.55],
        "p_value": [0.01, 0.08, 0.02],
    })
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / "partner_model_output.dta"
    df.to_stata(path, write_index=False)
    print(f"Wrote synthetic partner file: {path}")
    return path


def dta_to_canonical(dta_path: Path):
    """Convert .dta -> CSV (canonical, publishable format)."""
    df = pd.read_stata(dta_path)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / (dta_path.stem + ".csv")
    df.to_csv(out_path, index=False)
    print(f"Converted to canonical format: {out_path}")
    return df


if __name__ == "__main__":
    fake_path = make_fake_partner_dta()
    print(dta_to_canonical(fake_path))
