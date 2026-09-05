from __future__ import annotations

from .models import ConceptState


class MasteryEngine:
    """Small evidence-based mastery model suitable for the first prototype."""

    def update(
        self,
        state: ConceptState,
        *,
        correct: bool,
        misconception_id: str | None = None,
    ) -> ConceptState:
        state.evidence_count += 1
        if correct:
            state.mastery_probability += (1.0 - state.mastery_probability) * 0.45
            if misconception_id:
                state.misconceptions.discard(misconception_id)
        else:
            state.mastery_probability *= 0.65
            if misconception_id:
                state.misconceptions.add(misconception_id)
        state.mastery_probability = round(state.mastery_probability, 3)
        return state

