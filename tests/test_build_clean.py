from scripts.build_clean import build_panel


def test_build_panel_has_expected_shape_and_missing_values():
    panel = build_panel()

    assert len(panel) == 378
    assert panel["GeoID"].nunique() == 42
    assert panel["year"].nunique() == 9
    assert not panel.duplicated(["GeoID", "year"]).any()

    adult_columns = [
        "asthma_adult_rate_adj",
        "asthma_adult_rate_raw",
        "asthma_adult_n",
    ]
    adult_2015 = panel["year"].eq(2015)
    for column in adult_columns:
        assert panel[column].isna().equals(adult_2015)

    assert panel["asthma_child_rate_flagged"].eq(True).sum() == 3
