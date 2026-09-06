# WhyWrong

**Don't just correct mistakes. Understand them.**

WhyWrong is an AI learning debugger. It diagnoses the misconception behind a
student's wrong answer, asks a compact question that separates competing
hypotheses, teaches the detected gap, and then retries the original concept.

The demo includes four testable neural-network learning loops: backpropagation,
activation functions, learning rate, and overfitting.

## Milestone 1

The diagnostic core currently:

- classifies free-text answers against an explicit misconception library;
- keeps a probability distribution over competing hypotheses;
- selects a diagnostic probe by expected information gain;
- updates the hypotheses from the probe response;
- returns a targeted micro-lesson;
- updates concept mastery after a retry.
- lets learners switch among four concepts, each with its own competing
  misconceptions, diagnostic probe, and targeted repair.

The baseline is deterministic and local. With `OPENAI_API_KEY` configured, the
backend uses OpenAI Structured Outputs for free-text assessment. Misconception
IDs, probe selection, belief updates, and mastery remain application-controlled.
If the API is unavailable, the demo falls back to the deterministic baseline.
For a small public deployment, LLM calls are guarded by configurable per-IP and
per-session limits. Configure a hard project spend limit in the OpenAI dashboard
as the final backstop; the in-process limiter resets whenever the server restarts.

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

# Optional public-demo limits (defaults shown in .env.example)
# WHYWRONG_RATE_LIMIT=10
# WHYWRONG_RATE_WINDOW_SECONDS=60
# WHYWRONG_MAX_SESSION_ANALYSES=3

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

# Reproducible, free deterministic evaluation (48 labeled answers)
python -m backend.evaluation.run
```

## Evaluation

The checked-in evaluation set contains 48 answer variants balanced across
correct explanations, optimizer confusion, gradient misunderstanding, and
genuinely ambiguous responses. The generated Markdown and JSON reports make the
baseline reproducible for judges without an API key.

An OpenAI comparison is optional and never runs implicitly. Each evaluated row
is a paid API request, so it requires both a server-side `OPENAI_API_KEY` and an
explicit confirmation flag:

```bash
# Small paid smoke run
python -m backend.evaluation.run --provider openai --limit 4 --confirm-paid-run \
  --output docs/evaluation-openai-smoke.md

# Full paid comparison
python -m backend.evaluation.run --provider openai --confirm-paid-run \
  --output docs/evaluation-openai.md
```

The API key stays in the ignored `.env` file. It is not needed to run the local
baseline, tests, frontend, or deterministic fallback.

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
  evaluation/
    responses.json
    run.py
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
