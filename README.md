# BreatheNYC

An interactive NYC air quality and asthma explorer, with a grounded, evaluated AI question-answering layer.

Status: Phase 1 (Data) complete. Phase 2 (Analysis) next.

## How to run

Create and activate a virtual environment, then install the requirements:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Build the clean panel and run the tests:

```bash
python scripts/build_clean.py
pytest
```

Findings, accuracy, and screenshots will be added only after I have produced them.
