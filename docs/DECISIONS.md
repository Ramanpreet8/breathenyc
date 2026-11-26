# Decisions and open questions

## Decisions
1. Outcome = observed asthma ED visit rates (adults, ages 5-17). NOT the modeled "asthma ED visits due to PM2.5" indicator, because it is calculated from PM2.5 and would make the correlation circular.
2. Stop rule: if years or geography do not overlap across all three datasets, pick different data before building anything.
3. Scope: 2-3 indicators, one AI feature.

## Open questions
- ~~Which geography will all three indicators share?~~ Resolved in Update 2026-11-24: UHF42.
- ~~Which years will all three indicators share?~~ Resolved in Update 2026-11-24: 2015-2023.
- ~~Commit raw data to git or not? (Leaning yes if files are small, for reproducibility.)~~ Resolved in Update 2026-11-24: raw data committed to git.

## Update 2026-11-24
- Decision: shared geography = UHF42. CD fails on asthma and poverty years; NTA has no PM2.5.
- Decision: shared study years = 2015-2023.
- Decision: raw data committed to git for reproducibility.
- Decision: use "Neighborhood poverty" (percent), not "Child poverty (under age 5)".
- Open: rule for matching 5-year poverty windows to single years.
- Open: how to handle "*" flagged asthma values (3 rows in the age 5-17 UHF42 data).
- Open: adults asthma 2015 missing at UHF42; check the portal.

## Update 2026-11-25

### Poverty data matching
Poverty estimates are drawn from overlapping five-year American Community Survey (ACS) periods rather than annual estimates. To align poverty data with each study year, we assign the five-year ACS estimate ending in that year. For example, 2017 is matched to the 2013–2017 ACS estimate. This approach provides coverage for every year from 2015 through 2023 without requiring extrapolation beyond the available data.

Two limitations should be noted. First, because each estimate summarizes a five-year period, it reflects conditions preceding and including the matched year rather than conditions in that year alone. Second, consecutive annual estimates overlap substantially, sharing four of their five years of underlying data. Consequently, poverty estimates across neighboring years are not statistically independent.

As a robustness check, we plan to repeat the analysis using a consistent 2019–2023 ACS five-year estimate across all study years to assess whether the findings are sensitive to the year-specific matching approach.

### Flagged and missing asthma values
Three UHF42 rows in the ages 5-17 asthma file (Greenwich Village - SoHo in 2020 and 2021, and Bayside - Little Neck in 2020) are flagged with an asterisk. Each is based on only 4 or 5 visits, far fewer than any unflagged row, and their rates are well below those of the same neighborhoods in other years. These rows are kept in the dataset with a `flagged` indicator so they can be identified. As a robustness check, the analysis will be repeated with the flagged rows excluded.

The adult asthma file has no data for 2015 at any geographic level other than a citywide row without values. Adult asthma rates for 2015 are therefore left missing and are not imputed. PM2.5 and ages 5-17 data are retained for 2015, so the adult analysis covers 2016-2023 and the 5-17 analysis covers 2015-2023. This difference in year coverage is noted when reporting results.

### Adult asthma rate measure
The adult asthma ED visit file reports two rates per 10,000 residents: a raw estimated annual rate and an age-adjusted rate. Because this analysis compares neighborhoods, which differ in their age composition, we use the age-adjusted rate for adults. Age adjustment recalculates each neighborhood's rate as if all neighborhoods had the same age distribution, so differences between neighborhoods are less likely to reflect age mix alone. For ages 5-17, only the raw estimated annual rate is available, and it is used as is, since the group is already limited to a narrow age band.

Two limitations should be noted. First, the adult and child outcomes are different kinds of rates (age-adjusted versus raw), so their values should not be compared directly in size, only in how they relate to PM2.5 and poverty. Second, age adjustment depends on the standard population the portal chose, which this project does not control.

As a robustness check, we plan to repeat the adult analysis using the raw estimated annual rate to assess whether the findings are sensitive to this choice.

## Update 2026-11-26

### Time trends and the 2020-2021 pandemic years
Citywide PM2.5 and asthma ED rates both decline over 2015-2023, and ED visits drop sharply in 2020-2021 (COVID-19). A pooled correlation across all years would mostly reflect this shared time trend rather than differences between neighborhoods. Decision: models for RQ1 and RQ2 include year fixed effects (one indicator per year), so the PM2.5 association is estimated from differences between neighborhoods within the same year. Standard errors will be clustered by neighborhood, because each neighborhood appears up to 9 times. As a robustness check, the analysis will be repeated excluding 2020 and 2021.

This decision is recorded before any association between PM2.5 and asthma has been examined.
