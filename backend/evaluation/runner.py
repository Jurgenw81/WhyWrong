from __future__ import annotations

from backend.diagnostic.engine import DiagnosticEngine
from backend.diagnostic.llm_classifier import OpenAIAnswerClassifier
from backend.diagnostic.models import Analysis, NextAction

from .dataset import EvaluationExample
from .metrics import EvaluationResult, EvaluationSummary, summarize


def prediction_for(analysis: Analysis) -> str:
    if analysis.next_action is NextAction.PASS:
        return "correct"
    if not analysis.hypotheses:
        return "ambiguous"
    first, *rest = analysis.hypotheses
    runner_up = rest[0].probability if rest else 0.0
    if first.probability < 0.6 or first.probability - runner_up < 0.2:
        return "ambiguous"
    return first.id


def passes_expectation(expected: str, analysis: Analysis, predicted: str) -> bool:
    if expected == "ambiguous":
        return analysis.next_action is NextAction.PROBE
    return predicted == expected


async def evaluate(
    examples: tuple[EvaluationExample, ...],
    *,
    provider: str,
    classifier: OpenAIAnswerClassifier | None = None,
) -> EvaluationSummary:
    engine = DiagnosticEngine()
    if provider not in {"deterministic", "openai"}:
        raise ValueError("Provider must be 'deterministic' or 'openai'")
    if provider == "openai" and classifier is None:
        classifier = OpenAIAnswerClassifier.from_environment()
        if classifier is None:
            raise ValueError("OPENAI_API_KEY is required for an OpenAI evaluation")

    results = []
    for example in examples:
        if provider == "openai":
            assert classifier is not None
            analysis = await classifier.analyze(example.answer, engine)
        else:
            analysis = engine.analyze(example.answer)
        predicted = prediction_for(analysis)
        results.append(
            EvaluationResult(
                example_id=example.id,
                expected=example.label,
                predicted=predicted,
                passed=passes_expectation(example.label, analysis, predicted),
                source=analysis.source,
            )
        )
    return summarize(results)

