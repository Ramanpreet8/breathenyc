"""Fit year-fixed-effects OLS models with neighborhood-clustered errors."""
from collections.abc import Sequence
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parent.parent


def fit_model(
    panel: pd.DataFrame,
    outcome: str,
    controls: Sequence[str] = (),
) -> pd.DataFrame:
    """Estimate the PM2.5 coefficient and return its clustered inference."""
    controls = list(controls)
    required = list(dict.fromkeys([outcome, "pm25_annual", "year", "GeoID", *controls]))
    missing = [column for column in required if column not in panel.columns]
    if missing:
        raise ValueError(f"Missing model columns: {', '.join(missing)}")

    model_data = panel.dropna(subset=required).copy()
    if model_data.empty:
        raise ValueError("No complete rows are available for this model")

    predictors = ["pm25_annual", *controls, "C(year)"]
    formula = f"{outcome} ~ {' + '.join(predictors)}"
    result = smf.ols(formula=formula, data=model_data).fit(
        cov_type="cluster",
        cov_kwds={"groups": model_data["GeoID"]},
    )
    interval = result.conf_int().loc["pm25_annual"]

    return pd.DataFrame(
        [
            {
                "outcome": outcome,
                "term": "pm25_annual",
                "coefficient": result.params["pm25_annual"],
                "standard_error": result.bse["pm25_annual"],
                "ci_lower_95": interval.iloc[0],
                "ci_upper_95": interval.iloc[1],
                "p_value": result.pvalues["pm25_annual"],
                "n_rows": int(result.nobs),
                "n_clusters": model_data["GeoID"].nunique(),
            }
        ]
    )


def _named_model(
    panel: pd.DataFrame,
    specification: str,
    outcome: str,
    controls: Sequence[str],
) -> pd.DataFrame:
    result = fit_model(panel, outcome, controls)
    result.insert(0, "specification", specification)
    result.insert(2, "controls", ", ".join(controls) if controls else "none")
    return result


def run_sensitivity_models(panel: pd.DataFrame) -> pd.DataFrame:
    child_flagged = panel["asthma_child_rate_flagged"].eq(True)
    child_unflagged = panel.loc[~child_flagged]
    outside_pandemic_years = panel.loc[~panel["year"].isin([2020, 2021])]

    specifications = [
        ("Base", panel, "asthma_child_rate", []),
        ("Main", panel, "asthma_child_rate", ["poverty_pct"]),
        ("Robustness A", panel, "asthma_child_rate", ["poverty_pct_2019_23"]),
        ("Robustness B", child_unflagged, "asthma_child_rate", ["poverty_pct"]),
        ("Robustness D", outside_pandemic_years, "asthma_child_rate", ["poverty_pct"]),
        ("Base", panel, "asthma_adult_rate_adj", []),
        ("Main", panel, "asthma_adult_rate_adj", ["poverty_pct"]),
        ("Robustness A", panel, "asthma_adult_rate_adj", ["poverty_pct_2019_23"]),
        ("Robustness C", panel, "asthma_adult_rate_raw", ["poverty_pct"]),
        ("Robustness D", outside_pandemic_years, "asthma_adult_rate_adj", ["poverty_pct"]),
    ]
    return pd.concat(
        [
            _named_model(frame, name, outcome, controls)
            for name, frame, outcome, controls in specifications
        ],
        ignore_index=True,
    )


def within_year_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    """Return Pearson correlations between PM2.5 and poverty within each year."""
    rows = []
    for year, year_data in panel.groupby("year", sort=True):
        complete = year_data.dropna(subset=["pm25_annual", "poverty_pct"])
        rows.append(
            {
                "year": int(year),
                "pearson_r": complete["pm25_annual"].corr(complete["poverty_pct"]),
                "n_neighborhoods": complete["GeoID"].nunique(),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    panel = pd.read_csv(ROOT / "data" / "clean" / "uhf42_panel.csv")
    results = run_sensitivity_models(panel)
    correlations = within_year_correlations(panel)
    results.to_csv(ROOT / "data" / "clean" / "model_results.csv", index=False)
    print("Model results")
    print(results.to_string(index=False))
    print("\nWithin-year PM2.5-poverty correlations")
    print(correlations.to_string(index=False))
