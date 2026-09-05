# Development log

## 2026-09-05 — Milestone 1 foundation

- Started in a clean Git repository during the stated competition window.
- Defined the first backpropagation diagnostic interaction.
- Added explicit misconception hypotheses and deterministic baseline classifier.
- Added entropy-based diagnostic probe selection and Bayesian belief updates.
- Added targeted micro-lessons, mastery updates, CLI demo, and unit tests.

The deterministic baseline is intentional: it makes the learning loop testable before
an LLM-based free-text classifier is connected.

## 2026-09-05 — Probe input fix

- Made diagnostic choice input case-insensitive and whitespace-tolerant.
- Added regression coverage for lowercase, uppercase, and padded answers.

## 2026-09-05 — Diagnostic API

- Wrapped the diagnostic loop in a FastAPI application.
- Added in-memory learning sessions with explicit phase transitions.
- Added endpoints for session creation, initial answers, probes, retries, and state.
- Added API integration tests and reproducible project dependency metadata.

## 2026-09-05 — Knowledge MRI interface

- Added a responsive React/Vite interface for the complete diagnostic loop.
- Visualized prerequisite concepts and live mastery/misconception state changes.
- Added hypothesis confidence bars, diagnostic choices, micro-lesson, and retry state.
- Enabled local frontend-to-API requests with narrow development CORS origins.
