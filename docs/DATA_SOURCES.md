# Data sources

All files downloaded on 2026-11-24 from the NYC Environment & Health Data Portal
(https://a816-dohbesp.nyc.gov/IndicatorPublic/), via each indicator's Table tab > Download data.
Raw files in data/raw are untouched.

| File | Indicator | Source | Measure used | UHF42 years | Notes |
|---|---|---|---|---|---|
| pm25.csv | Fine particles (PM 2.5) | NYC Community Air Survey | Annual mean (mcg/m3) | 2015-2025 | |
| asthma_ed_5to17.csv | Asthma ED visits (age 5 to 17) | SPARCS hospital discharge data | Estimated annual rate per 10,000 | 2005-2023 | 3 values flagged with "*" |
| asthma_ed_adults.csv | Asthma ED visits (adults) | SPARCS hospital discharge data | Age-adjusted rate per 10,000 | 2005-2023 | 2015 missing in this file |
| poverty.csv | Neighborhood poverty | American Community Survey | Percent | 2007-11 to 2019-23 | 5-year overlapping windows, not single years |

## Not used
- "Asthma ED visits due to PM2.5" and "due to Ozone": modeled estimates, circular with PM2.5.
- "Regulatory PM2.5 monitoring": citywide only.
- "Child poverty (under age 5)": different population.
- "by NTA" asthma indicators: no PM2.5 data at NTA.

## Geography check (UHF42 vs CD)
- UHF42: all four files share the same 42 area IDs; PM2.5 and asthma overlap 2015-2023.
- CD: asthma only 2019-2023, poverty only to 2015-19, so it fails the overlap rule.
