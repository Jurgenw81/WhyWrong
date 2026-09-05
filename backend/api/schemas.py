from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    concept_id: str = "backpropagation"


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=2_000)


class HypothesisResponse(BaseModel):
    id: str
    label: str
    probability: float
    evidence: str


class ProbeResponse(BaseModel):
    id: str
    question: str
    choices: list[str]


class ConceptStateResponse(BaseModel):
    concept_id: str
    mastery_probability: float
    evidence_count: int
    misconceptions: list[str]


class SessionResponse(BaseModel):
    session_id: str
    concept_id: str
    concept_name: str
    question: str
    phase: Literal["question", "probe", "lesson", "complete"]
    state: ConceptStateResponse


class AnalysisResponse(BaseModel):
    session_id: str
    correctness: float
    reasoning_quality: float
    next_action: Literal["pass", "probe", "intervene"]
    hypotheses: list[HypothesisResponse]
    probe: ProbeResponse | None
    lesson: str | None = None
    misconception_id: str | None = None
    analysis_source: str
    state: ConceptStateResponse


class HealthResponse(BaseModel):
    status: Literal["ok"]
    classifier: Literal["deterministic", "openai"]
    model: str | None = None
