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

The first implementation is deterministic and local. Its interfaces are built
so an LLM classifier can be added later without giving the model control of the
learning loop.

## Run it

```bash
python3 -m backend.cli
python3 -m unittest discover -s backend/tests -v
```

## Project structure

```text
backend/
  cli.py
  curriculum/neural_networks.json
  diagnostic/
    engine.py
    mastery.py
    models.py
    probes.py
  tests/
docs/
  development-log.md
```

## Competition

Built for the Prometheus Fall Classic. The participant-provided deadline is
September 26, 2026, and the submission requires source code plus a demo video
of no more than two minutes.

