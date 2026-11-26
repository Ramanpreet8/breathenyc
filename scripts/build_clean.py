"""Build the clean UHF42 neighborhood-by-year analysis table."""
from pathlib import Path

import pandas as pd

if __package__:
    from .load_data import DATASETS, Dataset, load_one, uhf42
else:
    from load_data import DATASETS, Dataset, load_one, uhf42


ROOT = Path(__file__).resolve().parent.parent
START_YEAR = 2015
END_YEAR = 2023


def _prepare_dataset(dataset: Dataset) -> pd.DataFrame:
    rows = uhf42(load_one(dataset.name))
    if dataset.window_years:
        rows["poverty_window"] = rows["TimePeriod"]
        rows["year"] = 2000 + rows["TimePeriod"].str[-2:].astype(int)
    else:
        rows["year"] = rows["TimePeriod"].astype(int)
    rows = rows.loc[rows["year"].between(START_YEAR, END_YEAR)].copy()

    renames = dict(dataset.columns)
    for raw_column, clean_column in dataset.columns.items():
        flag_column = f"{raw_column}_flagged"
        if flag_column in rows.columns:
            renames[flag_column] = f"{clean_column}_flagged"
    if dataset.name == "pm25":
        renames["Geography"] = "neighborhood"
    rows = rows.rename(columns=renames)

    if dataset.name == "pm25":
        value_columns = [
            "GeoID",
            "neighborhood",
            "Borough",
            "year",
            *dataset.columns.values(),
        ]
    else:
        value_columns = ["GeoID", "year"]
        if dataset.window_years:
            value_columns.append("poverty_window")
        value_columns.extend(dataset.columns.values())
    flag_columns = [column for column in rows if column.endswith("_flagged")]
    return rows[value_columns + flag_columns]


def _drop_unneeded_flags(
    dataset: Dataset,
    frame: pd.DataFrame,
    child_name: str,
    child_rate_flag: str,
    child_count_flag: str,
) -> pd.DataFrame:
    flag_columns = [column for column in frame if column.endswith("_flagged")]
    for column in flag_columns:
        if dataset.name == child_name and column == child_rate_flag:
            continue
        if dataset.name == child_name and column == child_count_flag:
            # The portal marks both fields for the same low-count visits.
            assert frame[column].equals(frame[child_rate_flag])
        else:
            assert not frame[column].any(), (
                f"Unexpected flagged values in {dataset.name}.{column}"
            )
    drop_columns = [column for column in flag_columns if column != child_rate_flag]
    return frame.drop(columns=drop_columns)


def build_panel() -> pd.DataFrame:
    datasets = {dataset.name: dataset for dataset in DATASETS}
    frames = {
        dataset.name: _prepare_dataset(dataset)
        for dataset in DATASETS
    }

    child_dataset = datasets["asthma_ed_5to17"]
    child_rate_flag = (
        child_dataset.columns["Estimated annual rate per 10,000"] + "_flagged"
    )
    child_count_flag = child_dataset.columns["Number"] + "_flagged"
    for dataset in DATASETS:
        frames[dataset.name] = _drop_unneeded_flags(
            dataset,
            frames[dataset.name],
            child_dataset.name,
            child_rate_flag,
            child_count_flag,
        )

    panel = frames["pm25"]
    for dataset in DATASETS:
        if dataset.name == "pm25":
            continue
        panel = panel.merge(
            frames[dataset.name],
            on=["GeoID", "year"],
            how="left",
            validate="one_to_one",
        )
        print(f"Rows after {dataset.name} merge: {len(panel)}")

    poverty_dataset = datasets["poverty"]
    poverty_column = next(iter(poverty_dataset.columns.values()))
    poverty = frames[poverty_dataset.name]
    baseline = poverty.loc[
        poverty["poverty_window"].eq("2019-23"), ["GeoID", poverty_column]
    ]
    assert baseline["GeoID"].nunique() == 42
    assert not baseline["GeoID"].duplicated().any()
    baseline_values = baseline.set_index("GeoID")[poverty_column]
    panel["poverty_pct_2019_23"] = panel["GeoID"].map(baseline_values)

    panel = panel.sort_values(["GeoID", "year"]).reset_index(drop=True)

    assert len(panel) == 378, f"Expected 378 rows, got {len(panel)}"
    assert panel["GeoID"].nunique() == 42
    assert panel["year"].nunique() == 9
    assert not panel.duplicated(["GeoID", "year"]).any()

    adult_dataset = datasets["asthma_ed_adults"]
    adult_columns = list(adult_dataset.columns.values())
    adult_adjusted = adult_dataset.columns["Age-adjusted rate per 10,000"]
    adult_2015 = panel["year"].eq(2015)
    assert panel[adult_adjusted].isna().sum() == 42
    assert panel.loc[panel[adult_adjusted].isna(), "year"].eq(2015).all()
    for column in adult_columns:
        assert panel[column].isna().equals(adult_2015), (
            f"{column} should be missing only for the 2015 UHF42 rows"
        )

    other_columns = [
        column for column in panel.columns if column not in adult_columns
    ]
    assert not panel[other_columns].isna().any().any(), (
        "Unexpected missing values outside the 2015 adult asthma fields"
    )
    assert panel[child_rate_flag].eq(True).sum() == 3

    output_path = ROOT / "data" / "clean" / "uhf42_panel.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(output_path, index=False)

    print(
        f"Saved {len(panel)} rows for {panel['GeoID'].nunique()} neighborhoods "
        f"and {panel['year'].nunique()} years to {output_path.relative_to(ROOT)}"
    )
    print(f"Year range: {panel['year'].min()}-{panel['year'].max()}")
    print(f"Child asthma low-count rows: {panel[child_rate_flag].eq(True).sum()}")
    print(
        "Adult asthma 2015 rows left missing: "
        f"{panel.loc[adult_2015, adult_adjusted].isna().sum()}"
    )
    return panel


if __name__ == "__main__":
    build_panel()
