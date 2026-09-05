from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class NextAction(StrEnum):
    PASS = "pass"
    PROBE = "probe"
    INTERVENE = "intervene"


@dataclass(frozen=True)
class Hypothesis:
    id: str
    label: str
    probability: float
    evidence: str


@dataclass(frozen=True)
class Probe:
    id: str
    question: str
    choices: tuple[str, ...]
    likelihoods: dict[str, dict[str, float]]


@dataclass(frozen=True)
class Analysis:
    correctness: float
    reasoning_quality: float
    hypotheses: tuple[Hypothesis, ...]
    next_action: NextAction
    probe: Probe | None = None


@dataclass
class ConceptState:
    concept_id: str
    mastery_probability: float = 0.35
    evidence_count: int = 0
    misconceptions: set[str] = field(default_factory=set)

