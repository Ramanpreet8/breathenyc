# BreatheNYC

An interactive NYC air quality and asthma explorer, with a grounded, evaluated AI question-answering layer.

**Status:** Phase 1 (Data) & Phase 2 (Analysis) Complete. Phase 3 (API + DB) next.

---

## Overview

* **The Problem:** Asthma burden and air pollution are not distributed evenly across New York City. Residents, community organizers, and researchers have no unified, transparent way to see how their neighborhood compares or how health outcomes have shifted over time.
* **The Solution:** A full-stack web application where users can explore fine particulate matter ($\text{PM}_{2.5}$), observed asthma emergency department (ED) visit rates, and neighborhood poverty over time across a map and interactive trend charts. A grounded, evaluated AI assistant answers plain-English questions strictly from verified database records.
* **Why a Rebuild, Not a Copy:** Early student explorations often find no statistical link between air quality and asthma because raw datasets fail to overlap in years and geography, or they circularly correlate modeled outcomes derived from air sensors. BreatheNYC joins strictly overlapping indicators at the 42 United Hospital Fund (UHF42) neighborhood level across 2015–2023, controls for socioeconomic confounders, and packages honest empirical science into an accessible web platform.

---

## Key Empirical Findings

All econometric models are estimated with **year fixed effects** (to account for citywide temporal shocks such as COVID-19 lockdowns and post-pandemic recovery) and **neighborhood-clustered standard errors** (42 clusters):

1. **Research Question 1 (PM2.5 Association):**
   * **Pediatric Asthma (ages 5–17):** Unadjusted $\text{PM}_{2.5}$ coefficient: $+10.29$ visits per 10,000 per $1\ \mu\text{g}/\text{m}^3$ increase (95% CI: $[-17.94, +38.52]$, $p = 0.475$, $N = 378$).
   * **Adult Asthma (age-adjusted):** Unadjusted $\text{PM}_{2.5}$ coefficient: $-2.43$ visits per 10,000 (95% CI: $[-16.95, +12.08]$, $p = 0.743$, $N = 336$).
   * Both 95% confidence intervals cross zero: ambient outdoor $\text{PM}_{2.5}$ alone does not statistically drive neighborhood variation in ED visits within the same year.

2. **Research Question 2 (Controlling for Neighborhood Poverty):**
   * Controlling for annual poverty, the pediatric $\text{PM}_{2.5}$ coefficient remains non-significant at $+8.07$ (95% CI: $[-6.94, +23.09]$, $p = 0.292$).
   * Adult age-adjusted $\text{PM}_{2.5}$ coefficient remains non-significant at $-2.84$ (95% CI: $[-10.39, +4.72]$, $p = 0.462$).
   * Results remain consistent across four pre-specified robustness checks: (A) holding poverty fixed at 2019–23 baseline, (B) excluding 3 small-cell flagged pediatric rows, (C) using crude adult rates, and (D) dropping the 2020–2021 pandemic years.

3. **Research Question 3 (Descriptive Trends & The Spatial Paradox):**
   * **Citywide Air Quality Improvement:** Mean annual $\text{PM}_{2.5}$ declined by $\sim 24\%$ from $9.07\ \mu\text{g}/\text{m}^3$ in 2015 to $6.86\ \mu\text{g}/\text{m}^3$ in 2023, reaching a low of $6.08\ \mu\text{g}/\text{m}^3$ in 2022.
   * **The Pandemic Plunge:** Pediatric asthma ED visit rates dropped by $63\%$ in 2020 (from $141.2$ to $52.1$ per 10,000) due to school closures, masking, and hospital avoidance during COVID-19, with partial rebound to $133.0$ in 2023.
   * **The Geographic Disconnect:** The highest $\text{PM}_{2.5}$ levels are found in dense Midtown and Downtown Manhattan (Gramercy Park, Chelsea: $9.5\ \mu\text{g}/\text{m}^3$). Conversely, Greenwich Village has among the lowest asthma rates in NYC ($11.4$ adult, $26.8$ child). Asthma burden is heavily concentrated in the South Bronx and Upper Manhattan (Hunts Point, East Harlem: child rates $>340$, adult rates $>210$), reflecting deep structural inequalities in housing, poverty, and healthcare access.

---

## Data Pipeline & Architecture

| Layer | Technology | Status | Role |
|---|---|:---:|---|
| **Data Cleaning** | Python, Pandas | **Done** | Standardizes and joins 4 raw DOHMH portal CSVs into a balanced 378-row panel (`data/clean/uhf42_panel.csv`) |
| **Statistical Analysis** | Statsmodels, SciPy, Matplotlib | **Done** | Fixed-effects panel regressions, robustness checks, and trend audits |
| **Database** | PostgreSQL, Prisma | *Next* | Stores normalized `Neighborhood` and `AnnualMetric` tables |
| **API** | Express.js, Node.js | *Next* | Serves REST endpoints (`/api/neighborhoods`, `/api/trends`, `/api/ask`) |
| **Frontend** | React, Recharts, MapLibre | *Planned* | Interactive choropleth map, neighborhood selector, and trend charts |
| **Applied AI Layer** | Claude / Gemini API | *Planned* | Grounded natural language query engine with strict factual guardrails |
| **Evaluation Suite** | Python | *Planned* | 25-question ground-truth benchmark measuring retrieval and answer accuracy |

---

## How to Run Locally

### 1. Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Build Clean Panel Dataset
Rebuild the 378-row master panel from raw sources:
```bash
python scripts/build_clean.py
```

### 3. Run Econometric Models
Estimate the main regression specifications and robustness checks:
```bash
python scripts/analysis.py
```

### 4. Run Automated Test Suite
Run the test suite covering data loaders, schema assertions, and statistical models:
```bash
pytest
```

---

## Project Structure

```text
breathenyc/
├── data/
│   ├── raw/               # Immutable raw exports from NYC EH Data Portal
│   └── clean/             # Master panel dataset (uhf42_panel.csv) and model results
├── docs/
│   ├── DATA_SOURCES.md    # Source portal links, indicator IDs, and query terms
│   ├── DECISIONS.md       # Pre-analysis decisions (geography, poverty mapping, flags)
│   └── FINDINGS.md        # Complete empirical results and confidence intervals
├── notebooks/
│   ├── 01_audit.ipynb     # Initial data audit and shape verification
│   ├── 02_descriptive.ipynb # Time trends (RQ3) and neighborhood extremes
│   └── 03_analysis.ipynb  # Regression model coefficient visualizations
├── scripts/
│   ├── load_data.py       # Raw CSV loading and measure type conversions
│   ├── build_clean.py     # Panel construction, join validation, and integrity checks
│   └── analysis.py        # Clustered OLS panel regressions and robustness checks
└── tests/
    ├── test_load_data.py   # Loader unit tests
    ├── test_build_clean.py # Master panel shape and nullity tests
    └── test_analysis.py    # Regression parameter and correlation tests
```

---

## Limitations & Honest Reporting

* **Ecological Fallacy:** Neighborhood-level averages describe area burdens, not individual health risks. An individual living in a high-pollution area may have well-managed asthma, while an individual in a cleaner area may experience acute symptoms.
* **Emergency Department Visits vs. True Prevalence:** ED visit rates reflect severe, unmanaged asthma exacerbations and healthcare access patterns, not the total percentage of the population living with asthma.
* **Poverty Window Smoothing:** ACS poverty estimates are published as 5-year rolling averages (e.g., 2019–2023), which smooth over rapid annual economic shocks.
* **Correlation Does Not Equal Causation:** Observational associations should not be interpreted as causal relationships.

---

## AI Disclosure & Engineering Standards

In accordance with transparent research and modern software development practices:
* **Development Assistance:** AI developer tools (including Google Antigravity and GitHub Copilot) were utilized throughout this project for boilerplate generation, test case suggestions, and documentation refinement.
* **Human Ownership & Code Understanding:** Every data transformation, econometric model, and pipeline assertion was thoroughly vetted, simplified for explainability, and verified line-by-line. All analyses and architectural decisions are fully understood and can be defended in technical interviews.
* **Product AI Layer (Phase 5 Guardrails):** The planned conversational feature utilizes a strictly grounded retrieval pattern. The LLM is restricted to answering exclusively from SQL/API query outputs returned by our database, with built-in guardrails that refuse out-of-scope or unanswerable queries rather than hallucinating answers.
