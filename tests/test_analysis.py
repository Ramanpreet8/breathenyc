from pathlib import Path

import pandas as pd
import pytest

from scripts.analysis import (
    fit_model,
    run_sensitivity_models,
    within_year_correlations,
)


PANEL_PATH = Path(__file__).resolve().parents[1] / "data" / "clean" / "uhf42_panel.csv"
RESULT_COLUMNS = {
    "outcome",
    "term",
    "coefficient",
    "standard_error",
    "ci_lower_95",
    "ci_upper_95",
    "p_value",
    "n_rows",
    "n_clusters",
}


@pytest.mark.parametrize(
    ("outcome", "expected_rows"),
    [("asthma_child_rate", 378), ("asthma_adult_rate_adj", 336)],
)
def test_fit_model_returns_pm25_inference(outcome, expected_rows):
    panel = pd.read_csv(PANEL_PATH)

    result = fit_model(panel, outcome, controls=[])

    assert RESULT_COLUMNS.issubset(result.columns)
    assert len(result) == 1
    assert result.loc[0, "outcome"] == outcome
    assert result.loc[0, "term"] == "pm25_annual"
    assert result.loc[0, "n_rows"] == expected_rows
    assert result.loc[0, "n_clusters"] == 42


def test_sensitivity_models_and_within_year_correlations():
    panel = pd.read_csv(PANEL_PATH)

    results = run_sensitivity_models(panel)
    expected_models = {
        ("Base", "asthma_child_rate"),
        ("Main", "asthma_child_rate"),
        ("Robustness A", "asthma_child_rate"),
        ("Robustness B", "asthma_child_rate"),
        ("Robustness D", "asthma_child_rate"),
        ("Base", "asthma_adult_rate_adj"),
        ("Main", "asthma_adult_rate_adj"),
        ("Robustness A", "asthma_adult_rate_adj"),
        ("Robustness C", "asthma_adult_rate_raw"),
        ("Robustness D", "asthma_adult_rate_adj"),
    }

    assert set(zip(results["specification"], results["outcome"])) == expected_models
    assert results.loc[
        results["specification"].eq("Robustness B"), "n_rows"
    ].item() == 375

    correlations = within_year_correlations(panel)
    assert correlations["year"].tolist() == list(range(2015, 2024))
    assert correlations["n_neighborhoods"].tolist() == [42] * 9
