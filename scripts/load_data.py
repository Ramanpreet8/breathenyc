"""Read the four raw NYC EH Data Portal CSVs into clean pandas DataFrames.

Usage:
    from load_data import load_all, load_one     # in another script / notebook
    python scripts/load_data.py                   # prints a quick summary of each file

Raw files in data/raw are never modified; everything here is read-only.
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# short name -> raw file name (names follow docs/DATA_SOURCES.md)
FILES = {
    "pm25": "NYC EH Data Portal - Fine particles (PM 2.5) (filtered).csv",
    "asthma_ed_5to17": "NYC EH Data Portal - Asthma emergency department visits (age 5 to 17) (filtered).csv",
    "asthma_ed_adults": "NYC EH Data Portal - Asthma emergency department visits (adults) (filtered).csv",
    "poverty": "NYC EH Data Portal - Neighborhood poverty (filtered).csv",
}

# Columns 0-8 are identifiers (TimePeriod ... Area); everything after is a measure.
N_ID_COLS = 9


def load_one(name: str) -> pd.DataFrame:
    """Load one dataset by short name and clean the measure columns.

    Cleaning:
      - "41,772" -> 41772.0 (thousands commas removed)
      - "17.9*"  -> 17.9 and `flagged` = True (portal marks unstable/low-count estimates with "*")
      - "†"      -> NaN (value not reported)
    Original text is not kept; re-read the CSV if you need it.
    """
    df = pd.read_csv(
        RAW_DIR / FILES[name],
        dtype=str,
        keep_default_na=False,   # keep "-" and "" as text, we handle them ourselves
        encoding="utf-8-sig",
    )
    measure_cols = list(df.columns[N_ID_COLS:])

    df["flagged"] = False
    for col in measure_cols:
        s = df[col].str.strip()
        df["flagged"] |= s.str.endswith("*")
        s = s.str.replace("*", "", regex=False).str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(s, errors="coerce")   # "†" and blanks become NaN

    df["GeoID"] = pd.to_numeric(df["GeoID"], errors="coerce").astype("Int64")
    df["GeoRank"] = pd.to_numeric(df["GeoRank"], errors="coerce").astype("Int64")
    return df


def load_all() -> dict[str, pd.DataFrame]:
    """Load every dataset: {short_name: DataFrame}."""
    return {name: load_one(name) for name in FILES}


def uhf42(df: pd.DataFrame) -> pd.DataFrame:
    """Rows for the 42 UHF neighborhoods only (the shared geography, see DECISIONS.md)."""
    return df[df["GeoTypeDesc"] == "UHF 42"]


def _summary(name: str, df: pd.DataFrame) -> None:
    measure_cols = list(df.columns[N_ID_COLS:-1])  # skip the added `flagged` column
    print(f"\n=== {name}  ({len(df):,} rows)")
    print("columns:       ", ", ".join(df.columns[:N_ID_COLS]))
    print("measures:      ", ", ".join(measure_cols))
    print("geography:     ", df["GeoTypeDesc"].value_counts().to_dict())
    print("time periods:  ", f"{df['TimePeriod'].min()} -> {df['TimePeriod'].max()}",
          f"({df['TimePeriod'].nunique()} periods)")

    u = uhf42(df)
    years = sorted(u["TimePeriod"].unique())
    print("UHF42:         ", f"{u['GeoID'].nunique()} areas, {len(u):,} rows, "
          f"{years[0] if years else '-'} -> {years[-1] if years else '-'}")
    print("flagged (*):   ", int(df["flagged"].sum()), "rows overall,", int(u["flagged"].sum()), "in UHF42")
    print("missing values:", df[measure_cols].isna().sum().to_dict())


if __name__ == "__main__":
    data = load_all()
    for name, frame in data.items():
        _summary(name, frame)

