# Decisions and open questions

## Decisions
1. Outcome = observed asthma ED visit rates (adults, ages 5-17). NOT the modeled "asthma ED visits due to PM2.5" indicator, because it is calculated from PM2.5 and would make the correlation circular.
2. Stop rule: if years or geography do not overlap across all three datasets, pick different data before building anything.
3. Scope: 2-3 indicators, one AI feature.

## Open questions
- Which geography will all three indicators share?
- Which years will all three indicators share?
- Commit raw data to git or not? (Leaning yes if files are small, for reproducibility.)

## Update 2026-11-24
- Decision: shared geography = UHF42. CD fails on asthma and poverty years; NTA has no PM2.5.
- Decision: use "Neighborhood poverty" (percent), not "Child poverty (under age 5)".
- Open: rule for matching 5-year poverty windows to single years.
- Open: how to handle "*" flagged asthma values (3 rows in the age 5-17 UHF42 data).
- Open: adults asthma 2015 missing at UHF42; check the portal.

## Update 2026-11-25

### Poverty data matching
Poverty estimates are drawn from overlapping five-year American Community Survey (ACS) periods rather than annual estimates. To align poverty data with each study year, we assign the five-year ACS estimate ending in that year. For example, 2017 is matched to the 2013–2017 ACS estimate. This approach provides coverage for every year from 2015 through 2023 without requiring extrapolation beyond the available data.

Two limitations should be noted. First, because each estimate summarizes a five-year period, it reflects conditions preceding and including the matched year rather than conditions in that year alone. Second, consecutive annual estimates overlap substantially, sharing four of their five years of underlying data. Consequently, poverty estimates across neighboring years are not statistically independent.

As a robustness check, we plan to repeat the analysis using a consistent 2019–2023 ACS five-year estimate across all study years to assess whether the findings are sensitive to the year-specific matching approach.
