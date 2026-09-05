# WhyWrong

**Don't just correct mistakes. Understand them.**

WhyWrong is an AI learning debugger. It diagnoses the misconception behind a
student's wrong answer, asks a compact question that separates competing
hypotheses, teaches the detected gap, and then retries the original concept.

This repository starts with one deliberately narrow, testable learning loop:
distinguishing backpropagation from optimizer-driven parameter updates.

## Milestone 1

The diagnostic core currently:

- classifies free-text answers against an explicit misconception library;
- keeps a probability distribution over competing hypotheses;
- selects a diagnostic probe by expected information gain;
- updates the hypotheses from the probe response;
- returns a targeted micro-lesson;
- updates concept mastery after a retry.

The baseline is deterministic and local. With `OPENAI_API_KEY` configured, the
backend uses OpenAI Structured Outputs for free-text assessment. Misconception
IDs, probe selection, belief updates, and mastery remain application-controlled.
If the API is unavailable, the demo falls back to the deterministic baseline.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

# Optional: enable structured OpenAI classification
cp .env.example .env
# Add OPENAI_API_KEY to .env, then load it:
set -a
source .env
set +a

# Interactive terminal prototype
python -m backend.cli

# HTTP API and interactive docs
uvicorn backend.api.main:app --reload
# Open http://127.0.0.1:8000/docs

# In a second terminal: visual application
cd frontend
npm install
npm run dev
# Open http://127.0.0.1:5173

# Tests
python -m unittest discover -s backend/tests -v
```

## Project structure

```text
backend/
  api/
    main.py
    schemas.py
    store.py
  cli.py
  curriculum/neural_networks.json
  diagnostic/
    engine.py
    mastery.py
    models.py
    probes.py
  tests/
frontend/
  src/
    components/
docs/
  development-log.md
```

## Competition

Built for the Prometheus Fall Classic. The participant-provided deadline is
September 26, 2026, and the submission requires source code plus a demo video
of no more than two minutes.
