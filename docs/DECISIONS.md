# Decisions and open questions

## Decisions
1. Outcome = observed asthma ED visit rates (adults, ages 5-17). NOT the modeled "asthma ED visits due to PM2.5" indicator, because it is calculated from PM2.5 and would make the correlation circular.
2. Stop rule: if years or geography do not overlap across all three datasets, pick different data before building anything.
3. Scope: 2-3 indicators, one AI feature.

## Open questions
- Which geography will all three indicators share?
- Which years will all three indicators share?
- Commit raw data to git or not? (Leaning yes if files are small, for reproducibility.)
