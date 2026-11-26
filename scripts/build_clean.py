"""Build the clean UHF42 neighborhood-by-year analysis table."""
from pathlib import Path

import pandas as pd

if __package__:
    from .load_data import load_one, uhf42
else:
    from load_data import load_one, uhf42


ROOT = Path(__file__).resolve().parent.parent
START_YEAR = 2015
END_YEAR = 2023


def _prep_pm25() -> pd.DataFrame:
    df = uhf42(load_one("pm25"))
    df["year"] = df["TimePeriod"].astype(int)
    df = df.loc[df["year"].between(START_YEAR, END_YEAR)].copy()
    df = df.rename(
        columns={
            "Geography": "neighborhood",
            "Annual mean mcg/m3": "pm25_annual",
        }
    )
    return df[["GeoID", "neighborhood", "Borough", "year", "pm25_annual"]]


def _prep_child_asthma() -> pd.DataFrame:
    df = uhf42(load_one("asthma_ed_5to17"))
    df["year"] = df["TimePeriod"].astype(int)
    df = df.loc[df["year"].between(START_YEAR, END_YEAR)].copy()
    # In pediatric asthma, both rate and count are flagged on the exact same 3 low-count rows
    assert df["Number_flagged"].equals(
        df["Estimated annual rate per 10,000_flagged"]
    )
    df = df.rename(
        columns={
            "Estimated annual rate per 10,000": "asthma_child_rate",
            "Estimated annual rate per 10,000_flagged": "asthma_child_rate_flagged",
            "Number": "asthma_child_n",
        }
    )
    return df[
        [
            "GeoID",
            "year",
            "asthma_child_rate",
            "asthma_child_n",
            "asthma_child_rate_flagged",
        ]
    ]


def _prep_adult_asthma() -> pd.DataFrame:
    df = uhf42(load_one("asthma_ed_adults"))
    df["year"] = df["TimePeriod"].astype(int)
    df = df.loc[df["year"].between(START_YEAR, END_YEAR)].copy()
    df = df.rename(
        columns={
            "Age-adjusted rate per 10,000": "asthma_adult_rate_adj",
            "Estimated annual rate per 10,000": "asthma_adult_rate_raw",
            "Number": "asthma_adult_n",
        }
    )
    return df[
        [
            "GeoID",
            "year",
            "asthma_adult_rate_adj",
            "asthma_adult_rate_raw",
            "asthma_adult_n",
        ]
    ]


def _prep_poverty() -> pd.DataFrame:
    df = uhf42(load_one("poverty"))
    df["poverty_window"] = df["TimePeriod"]
    # Map 5-year rolling period to end year (e.g. '2019-23' -> 2023)
    end_years = df["TimePeriod"].str.split("-").str[1]
    df["year"] = ("20" + end_years).astype(int)
    df = df.loc[df["year"].between(START_YEAR, END_YEAR)].copy()
    df = df.rename(columns={"Percent": "poverty_pct"})
    return df[["GeoID", "year", "poverty_window", "poverty_pct"]]


def build_panel() -> pd.DataFrame:
    pm25 = _prep_pm25()
    child = _prep_child_asthma()
    adult = _prep_adult_asthma()
    poverty = _prep_poverty()

    panel = (
        pm25.merge(child, on=["GeoID", "year"], how="left", validate="one_to_one")
        .merge(adult, on=["GeoID", "year"], how="left", validate="one_to_one")
        .merge(poverty, on=["GeoID", "year"], how="left", validate="one_to_one")
    )

    # Pre-pandemic 2019-23 baseline poverty for Robustness A
    baseline = poverty.loc[
        poverty["poverty_window"].eq("2019-23"), ["GeoID", "poverty_pct"]
    ]
    assert baseline["GeoID"].nunique() == 42
    assert not baseline["GeoID"].duplicated().any()
    baseline_values = baseline.set_index("GeoID")["poverty_pct"]
    panel["poverty_pct_2019_23"] = panel["GeoID"].map(baseline_values)

    panel = panel.sort_values(["GeoID", "year"]).reset_index(drop=True)

    assert len(panel) == 378, f"Expected 378 rows, got {len(panel)}"
    assert panel["GeoID"].nunique() == 42
    assert panel["year"].nunique() == 9
    assert not panel.duplicated(["GeoID", "year"]).any()

    adult_columns = [
        "asthma_adult_rate_adj",
        "asthma_adult_rate_raw",
        "asthma_adult_n",
    ]
    adult_2015 = panel["year"].eq(2015)
    assert panel["asthma_adult_rate_adj"].isna().sum() == 42
    assert panel.loc[adult_2015, "asthma_adult_rate_adj"].isna().all()
    for column in adult_columns:
        assert panel.loc[adult_2015, column].isna().all(), (
            f"{column} should be missing for 2015"
        )
        assert panel.loc[~adult_2015, column].notna().all(), (
            f"{column} should be non-missing outside 2015"
        )

    other_columns = [
        column for column in panel.columns if column not in adult_columns
    ]
    assert panel[other_columns].isna().sum().sum() == 0, (
        "Unexpected missing values outside the 2015 adult asthma fields"
    )
    assert panel["asthma_child_rate_flagged"].eq(True).sum() == 3

    output_path = ROOT / "data" / "clean" / "uhf42_panel.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(output_path, index=False)

    print(
        f"Saved {len(panel)} rows for {panel['GeoID'].nunique()} neighborhoods "
        f"and {panel['year'].nunique()} years to {output_path.relative_to(ROOT)}"
    )
    print(f"Year range: {panel['year'].min()}-{panel['year'].max()}")
    print(
        "Child asthma low-count rows: "
        f"{panel['asthma_child_rate_flagged'].eq(True).sum()}"
    )
    print(
        "Adult asthma 2015 rows left missing: "
        f"{panel.loc[adult_2015, 'asthma_adult_rate_adj'].isna().sum()}"
    )
    return panel


if __name__ == "__main__":
    build_panel()
