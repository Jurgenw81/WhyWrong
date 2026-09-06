from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    example_id: str
    expected: str
    predicted: str
    passed: bool
    source: str


@dataclass(frozen=True)
class EvaluationSummary:
    total: int
    passed: int
    accuracy: float
    per_label: dict[str, dict[str, float | int]]
    confusion: dict[str, dict[str, int]]
    results: tuple[EvaluationResult, ...]


def summarize(results: list[EvaluationResult]) -> EvaluationSummary:
    if not results:
        raise ValueError("Cannot summarize an empty result set")

    grouped: dict[str, list[EvaluationResult]] = defaultdict(list)
    confusion_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for result in results:
        grouped[result.expected].append(result)
        confusion_counts[result.expected][result.predicted] += 1

    per_label = {}
    for label, items in sorted(grouped.items()):
        passed = sum(item.passed for item in items)
        per_label[label] = {
            "total": len(items),
            "passed": passed,
            "accuracy": round(passed / len(items), 4),
        }

    passed = sum(result.passed for result in results)
    return EvaluationSummary(
        total=len(results),
        passed=passed,
        accuracy=round(passed / len(results), 4),
        per_label=per_label,
        confusion={
            expected: dict(sorted(predictions.items()))
            for expected, predictions in sorted(confusion_counts.items())
        },
        results=tuple(results),
    )

