from __future__ import annotations

import os
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from .engine import (
    DiagnosticEngine,
    GRADIENT_MISUNDERSTANDING,
    OPTIMIZER_CONFUSION,
)
from .models import Analysis


class MisconceptionAssessment(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    probability: float = Field(ge=0, le=1)
    evidence: str = Field(min_length=1, max_length=300)


class StructuredAssessment(BaseModel):
    correctness: float = Field(ge=0, le=1)
    reasoning_quality: float = Field(ge=0, le=1)
    misconceptions: list[MisconceptionAssessment] = Field(min_length=2, max_length=2)


INSTRUCTIONS = """You classify a student's conceptual understanding of backpropagation.

Evaluate only the supplied student answer against this reference distinction:
- Backpropagation computes gradients of loss with respect to parameters.
- A separate optimizer consumes gradients and updates parameters.

Score correctness and reasoning quality from 0 to 1. Assign probabilities to exactly
these two possible misconceptions: optimizer_confusion (attributes parameter updates
to backpropagation) and gradient_misunderstanding (treats a gradient as the update
itself). Evidence must briefly quote or paraphrase only the student's answer. When the
answer is correct, misconception probabilities should be low. When it is ambiguous,
keep confidence moderate rather than inventing intent."""


def instructions_for(engine: object) -> str:
    diagnostic = getattr(engine, "diagnostic", None)
    if diagnostic is None:
        return INSTRUCTIONS
    options = "\n".join(f"- {item[0]}: {item[1]}" for item in diagnostic.hypotheses)
    return f"""You diagnose a beginner's conceptual understanding of a neural-network topic.

Score correctness and reasoning quality from 0 to 1. Return exactly these two
misconception IDs, each with a probability and brief evidence grounded only in the answer:
{options}

Use only those exact IDs. When the answer is correct, misconception probabilities
should be low. When it is vague, keep confidence moderate rather than inventing intent."""


class OpenAIAnswerClassifier:
    def __init__(
        self,
        *,
        client: AsyncOpenAI | None = None,
        model: str = "gpt-5.4-mini",
    ) -> None:
        self.client = client or AsyncOpenAI(timeout=15.0, max_retries=1)
        self.model = model

    @classmethod
    def from_environment(cls) -> OpenAIAnswerClassifier | None:
        if not os.getenv("OPENAI_API_KEY"):
            return None
        return cls(model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"))

    async def analyze(
        self, answer: str, engine: DiagnosticEngine
    ) -> Analysis:
        response = await self.client.responses.parse(
            model=self.model,
            instructions=instructions_for(engine),
            input=answer,
            text_format=StructuredAssessment,
            store=False,
        )
        assessment = response.output_parsed
        if assessment is None:
            raise ValueError("The model returned no structured assessment")

        by_id = {item.id: item for item in assessment.misconceptions}
        diagnostic = getattr(engine, "diagnostic", None)
        supported = (
            [item[0] for item in diagnostic.hypotheses]
            if diagnostic is not None
            else [OPTIMIZER_CONFUSION, GRADIENT_MISUNDERSTANDING]
        )
        probabilities = {
            key: by_id[key].probability if key in by_id else 0 for key in supported
        }
        evidence = {
            hypothesis_id: item.evidence for hypothesis_id, item in by_id.items()
        }
        return engine.from_classification(
            correctness=assessment.correctness,
            reasoning_quality=assessment.reasoning_quality,
            probabilities=probabilities,
            evidence=evidence,
            source=f"openai:{self.model}",
        )
