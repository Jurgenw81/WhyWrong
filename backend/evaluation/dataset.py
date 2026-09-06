from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DATASET_PATH = Path(__file__).with_name("responses.json")
VALID_LABELS = {
    "correct",
    "optimizer_confusion",
    "gradient_misunderstanding",
    "ambiguous",
}


@dataclass(frozen=True)
class EvaluationExample:
    id: str
    answer: str
    label: str


def load_dataset(path: Path = DATASET_PATH) -> tuple[EvaluationExample, ...]:
    raw_examples = json.loads(path.read_text(encoding="utf-8"))
    examples = tuple(EvaluationExample(**item) for item in raw_examples)
    ids = [item.id for item in examples]
    if len(ids) != len(set(ids)):
        raise ValueError("Evaluation example IDs must be unique")
    unknown_labels = {item.label for item in examples} - VALID_LABELS
    if unknown_labels:
        raise ValueError(f"Unknown evaluation labels: {sorted(unknown_labels)}")
    if not examples:
        raise ValueError("Evaluation dataset cannot be empty")
    return examples

