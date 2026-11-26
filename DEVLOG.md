# DEVLOG

What I did, what broke, what I learned.

## Day 1
- Created the repo and folder structure.

## Day 2
- Found the right PM2.5 indicator (Fine particles, NYC Community Air Survey) after the first search only returned modeled and citywide ones.
- Downloaded four raw files and checked years and geography. UHF42 overlaps; CD does not.
- Learned: the Data index export is only a list of indicators; the real data comes from each indicator's Table tab.

## Day 3 (2026-11-25)
- Wrote the loader and audited all four files for shape, years, flags, duplicates, and ID matches.
- Decided poverty matching, flagged/missing value handling, and the adult age-adjusted rate.

## Day 4 (2026-11-26)
- Fixed audit notes and built `data/clean/uhf42_panel.csv` with assertions.
- Recorded the year-fixed-effects decision.
