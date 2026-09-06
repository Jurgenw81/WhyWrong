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

## 2026-09-05 — Structured LLM classification

- Added an optional OpenAI Responses API classifier using strict Pydantic output.
- Kept misconception IDs, probe selection, belief updates, and mastery app-controlled.
- Added explicit source metadata and deterministic fallback for demo resilience.
- Added mocked classifier tests; real API credentials remain server-side and uncommitted.

## 2026-09-06 — Public demo safeguards

- Added per-client sliding-window limits around paid classifier calls.
- Added a per-session analysis ceiling to constrain repeated requests.
- Bounded OpenAI request timeouts and retries for predictable demo behavior.
- Documented the in-process limiter boundary and dashboard spend-limit backstop.

## 2026-09-06 — Reproducible evaluation

- Added a checked-in, balanced dataset of 48 labeled student answers.
- Added deterministic and optional OpenAI evaluation runners with per-label metrics.
- Added Markdown and JSON reports suitable for the repository and submission evidence.
- Required an explicit paid-run flag before an evaluation can make OpenAI requests.

## 2026-09-06 — Neural-network question bank

- Expanded the demo from one concept to four: backpropagation, activation functions,
  learning rate, and overfitting.
- Added concept-specific misconception hypotheses, separating probes, and micro-lessons.
- Added an API concept catalog and a responsive topic selector with contextual maps.

## 2026-09-06 — Beginner course pathway

- Expanded the question bank to twelve connected lessons covering the full training loop.
- Added plain-language explanations, concrete examples, and explicit concept connections.
- Reworked navigation into a staged beginner curriculum with progress and next-lesson flow.
- Ensured every topic has its own misconception hypotheses, diagnostic probe, and repair.

## 2026-09-06 — Evidence-backed knowledge states

- Removed hardcoded prerequisite mastery claims from the knowledge map.
- Replaced the arbitrary initial percentage with explicit assessment status.
- Limited demonstrated and misconception states to evidence produced in the current session.

## 2026-09-06 — Course layout repair

- Removed the collision-prone floating concept graph from the main learning surface.
- Rebuilt the page as a stable two-column curriculum and lesson layout.
- Added explicit lesson numbering and a course progress indicator.
- Increased reading width and added narrow-screen stacking without overlays.
