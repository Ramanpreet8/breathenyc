# Research questions

Written on 2026-11-24, before any analysis, so the questions are fixed before results are seen.

Unit of analysis: UHF42 neighborhood x year (42 neighborhoods).

## RQ1 (main)
Are higher annual mean PM2.5 levels associated with higher observed asthma ED visit rates
in NYC neighborhoods, for ages 5-17 and for adults?

## RQ2 (confounding)
Does the PM2.5-asthma association remain after controlling for neighborhood poverty?

## RQ3 (descriptive)
How did PM2.5 and asthma ED rates change over 2015-2023, and which neighborhoods are highest?

## RQ4 (product)
Can a natural-language assistant answer only from rows returned by the API, and refuse
when the data cannot answer? Measured on a 25-question ground-truth set.

## Hypothesis (to be tested, not assumed)
Higher PM2.5 is associated with higher asthma ED rates, and the association is weaker once
poverty is controlled for. A null or small result is an acceptable outcome and will be reported as found.

## What this project cannot show
- Correlation is not causation.
- Neighborhood-level data cannot describe individuals (ecological fallacy).
- Poverty is measured in overlapping 5-year windows, so it is a rough control.
- Outcome is observed ED visits only, not asthma prevalence.
