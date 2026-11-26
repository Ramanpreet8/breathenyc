import pandas as pd
import pytest

from scripts.load_data import (
    DATASETS,
    clean_measures,
    get_dataset,
    load_all,
    load_one,
    uhf42,
)


def test_clean_measures_parses_commas_stars_and_suppressed_values():
    raw = pd.DataFrame(
        {
            "Number": ["41,772"],
            "Rate": ["17.9*"],
            "Percent": ["†"],
        }
    )

    cleaned = clean_measures(raw)

    assert cleaned.loc[0, "Number"] == 41772
    assert cleaned.loc[0, "Rate"] == 17.9
    assert cleaned.loc[0, "Rate_flagged"]
    assert pd.isna(cleaned.loc[0, "Percent"])


def test_every_dataset_loads_with_42_uhf42_areas():
    data = load_all()

    assert set(data) == {dataset.name for dataset in DATASETS}
    for dataset in DATASETS:
        frame = data[dataset.name]
        assert not frame.empty
        assert uhf42(frame)["GeoID"].nunique() == 42


def test_child_asthma_has_expected_flagged_rows():
    dataset = get_dataset("asthma_ed_5to17")
    child = uhf42(load_one(dataset.name))
    flag_cols = [f"{column}_flagged" for column in dataset.columns]
    flagged = child.loc[child[flag_cols].any(axis=1), ["GeoID", "TimePeriod"]]

    observed = set(zip(flagged["GeoID"].astype(int), flagged["TimePeriod"]))
    assert len(flagged) == 3
    assert observed == {(308, "2020"), (308, "2021"), (404, "2020")}


def test_get_dataset_rejects_unknown_name():
    with pytest.raises(KeyError, match="Valid names"):
        get_dataset("nope")
