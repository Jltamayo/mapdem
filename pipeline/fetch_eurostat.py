"""
Skeleton ETL for Eurostat REGIO data. Unlike partner-delivered data (ESS,
GDELT, media deserts), Eurostat's API is public today, so this script is
runnable now, not just a stub. Output goes to data/raw/ because it is not
yet harmonised/joined to region geometry — it becomes a docs/ layer only
after passing through analysis/ (composite_index.R or equivalent).

Example dataset codes to try once partners confirm the final indicator list:
    - "tgs00010"  Disposable household income by NUTS2
    - "lfst_r_lfu3rt"  Unemployment rate by NUTS2

Run:
    pip install eurostat
    python pipeline/fetch_eurostat.py --dataset tgs00010
"""
import argparse
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch(dataset_code: str) -> pd.DataFrame:
    try:
        import eurostat
    except ImportError as e:
        raise SystemExit("Install the 'eurostat' package first: pip install eurostat") from e
    return eurostat.get_data_df(dataset_code)


def save(df: pd.DataFrame, dataset_code: str):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"eurostat_{dataset_code}.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Eurostat dataset code, e.g. tgs00010")
    args = parser.parse_args()
    save(fetch(args.dataset), args.dataset)
