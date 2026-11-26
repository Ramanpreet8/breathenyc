"""Build the clean UHF42 neighborhood-by-year analysis table."""
from pathlib import Path

from load_data import load_all, uhf42


ROOT = Path(__file__).resolve().parent.parent
START_YEAR = 2015
END_YEAR = 2023


def _annual_rows(frame):
    rows = uhf42(frame).copy()
    rows["year"] = rows["TimePeriod"].astype(int)
    return rows.loc[rows["year"].between(START_YEAR, END_YEAR)]


def build_panel():
    data = load_all()

    pm25 = _annual_rows(data["pm25"])[
        ["GeoID", "Geography", "Borough", "year", "Annual mean mcg/m3"]
    ].rename(
        columns={
            "Geography": "neighborhood",
            "Annual mean mcg/m3": "pm25_annual",
        }
    )
    child = _annual_rows(data["asthma_ed_5to17"])[
        [
            "GeoID",
            "year",
            "Estimated annual rate per 10,000",
            "Number",
            "flagged",
        ]
    ].rename(
        columns={
            "Estimated annual rate per 10,000": "asthma_child_rate",
            "Number": "asthma_child_n",
            "flagged": "asthma_child_flagged",
        }
    )
    adults = _annual_rows(data["asthma_ed_adults"])[
        [
            "GeoID",
            "year",
            "Age-adjusted rate per 10,000",
            "Estimated annual rate per 10,000",
            "Number",
        ]
    ].rename(
        columns={
            "Age-adjusted rate per 10,000": "asthma_adult_rate_adj",
            "Estimated annual rate per 10,000": "asthma_adult_rate_raw",
            "Number": "asthma_adult_n",
        }
    )

    poverty = uhf42(data["poverty"]).copy()
    poverty["poverty_window"] = poverty["TimePeriod"]
    poverty["year"] = 2000 + poverty["poverty_window"].str[-2:].astype(int)
    poverty = poverty.loc[poverty["year"].between(START_YEAR, END_YEAR)]
    poverty = poverty[
        ["GeoID", "year", "poverty_window", "Percent"]
    ].rename(columns={"Percent": "poverty_pct"})

    panel = pm25.merge(
        child, on=["GeoID", "year"], how="left", validate="one_to_one"
    )
    print(f"Rows after child asthma merge: {len(panel)}")
    panel = panel.merge(
        adults, on=["GeoID", "year"], how="left", validate="one_to_one"
    )
    print(f"Rows after adult asthma merge: {len(panel)}")
    panel = panel.merge(
        poverty, on=["GeoID", "year"], how="left", validate="one_to_one"
    )
    print(f"Rows after poverty merge: {len(panel)}")

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
    assert panel.loc[
        panel["asthma_adult_rate_adj"].isna(), "year"
    ].eq(2015).all()
    for column in adult_columns:
        assert panel[column].isna().equals(adult_2015), (
            f"{column} should be missing only for the 2015 UHF42 rows"
        )

    other_columns = [column for column in panel.columns if column not in adult_columns]
    assert not panel[other_columns].isna().any().any(), (
        "Unexpected missing values outside the 2015 adult asthma fields"
    )
    assert panel["asthma_child_flagged"].eq(True).sum() == 3

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
        f"{panel['asthma_child_flagged'].eq(True).sum()}"
    )
    print(
        "Adult asthma 2015 rows left missing: "
        f"{panel.loc[adult_2015, 'asthma_adult_rate_adj'].isna().sum()}"
    )
    return panel


if __name__ == "__main__":
    build_panel()
