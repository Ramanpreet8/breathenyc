"""Read the four raw NYC EH Data Portal CSVs into clean pandas DataFrames.

Usage:
    from load_data import load_all, load_one
    python scripts/load_data.py

Raw files in data/raw are never modified; everything here is read-only.
"""
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

ID_COLS = [
    "TimePeriod",
    "GeoTypePretty",
    "GeoTypeDesc",
    "GeoID",
    "GeoRank",
    "BoroID",
    "Borough",
    "Geography",
    "Area",
]


@dataclass(frozen=True)
class Dataset:
    name: str
    file: str
    columns: dict[str, str]
    window_years: bool = False

    @property
    def path(self) -> Path:
        return RAW_DIR / self.file


DATASETS = [
    Dataset(
        name="pm25",
        file="NYC EH Data Portal - Fine particles (PM 2.5) (filtered).csv",
        columns={"Annual mean mcg/m3": "pm25_annual"},
    ),
    Dataset(
        name="asthma_ed_5to17",
        file="NYC EH Data Portal - Asthma emergency department visits (age 5 to 17) (filtered).csv",
        columns={
            "Estimated annual rate per 10,000": "asthma_child_rate",
            "Number": "asthma_child_n",
        },
    ),
    Dataset(
        name="asthma_ed_adults",
        file="NYC EH Data Portal - Asthma emergency department visits (adults) (filtered).csv",
        columns={
            "Age-adjusted rate per 10,000": "asthma_adult_rate_adj",
            "Estimated annual rate per 10,000": "asthma_adult_rate_raw",
            "Number": "asthma_adult_n",
        },
    ),
    Dataset(
        name="poverty",
        file="NYC EH Data Portal - Neighborhood poverty (filtered).csv",
        columns={"Percent": "poverty_pct"},
        window_years=True,
    ),
]


def get_dataset(name: str) -> Dataset:
    for dataset in DATASETS:
        if dataset.name == name:
            return dataset
    valid_names = ", ".join(dataset.name for dataset in DATASETS)
    raise KeyError(f"Unknown dataset {name!r}. Valid names: {valid_names}")


def clean_measures(df: pd.DataFrame) -> pd.DataFrame:
    """Convert raw measure text to numbers and add per-measure flags."""
    cleaned = df.copy()
    measure_cols = [column for column in cleaned.columns if column not in ID_COLS]
    for column in measure_cols:
        values = cleaned[column].str.strip()
        cleaned[f"{column}_flagged"] = values.str.endswith("*")
        values = values.str.replace("*", "", regex=False).str.replace(
            ",", "", regex=False
        )
        cleaned[column] = pd.to_numeric(values, errors="coerce")
    return cleaned


def load_one(name: str) -> pd.DataFrame:
    """Load one dataset by short name and clean its measure columns."""
    dataset = get_dataset(name)
    df = pd.read_csv(
        dataset.path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )
    missing_ids = [column for column in ID_COLS if column not in df.columns]
    if missing_ids:
        raise ValueError(
            f"{dataset.file}: missing required ID column(s): "
            f"{', '.join(missing_ids)}"
        )

    df = clean_measures(df)
    df["GeoID"] = pd.to_numeric(df["GeoID"], errors="coerce").astype("Int64")
    df["GeoRank"] = pd.to_numeric(df["GeoRank"], errors="coerce").astype("Int64")
    return df


def load_all() -> dict[str, pd.DataFrame]:
    """Load every dataset: {short_name: DataFrame}."""
    return {dataset.name: load_one(dataset.name) for dataset in DATASETS}


def uhf42(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows for the 42 UHF neighborhoods."""
    return df.loc[df["GeoTypeDesc"] == "UHF 42"].copy()


def _summary(name: str, df: pd.DataFrame) -> None:
    flag_cols = [column for column in df.columns if column.endswith("_flagged")]
    measure_cols = [
        column
        for column in df.columns
        if column not in ID_COLS and column not in flag_cols
    ]
    print(f"\n=== {name}  ({len(df):,} rows)")
    print("columns:       ", ", ".join(column for column in ID_COLS if column in df))
    print("measures:      ", ", ".join(measure_cols))
    print("geography:     ", df["GeoTypeDesc"].value_counts().to_dict())
    print(
        "time periods:  ",
        f"{df['TimePeriod'].min()} -> {df['TimePeriod'].max()}",
        f"({df['TimePeriod'].nunique()} periods)",
    )

    u = uhf42(df)
    years = sorted(u["TimePeriod"].unique())
    print(
        "UHF42:         ",
        f"{u['GeoID'].nunique()} areas, {len(u):,} rows, "
        f"{years[0] if years else '-'} -> {years[-1] if years else '-'}",
    )
    print("flagged (*):   ", {column: int(df[column].sum()) for column in flag_cols})
    print(
        "flagged UHF42:",
        {column: int(u[column].sum()) for column in flag_cols},
    )
    print("missing values:", df[measure_cols].isna().sum().to_dict())


if __name__ == "__main__":
    for name, frame in load_all().items():
        _summary(name, frame)
