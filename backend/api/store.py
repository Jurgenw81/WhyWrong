from __future__ import annotations

from dataclasses import dataclass

from backend.diagnostic.models import Analysis, ConceptState


@dataclass
class LearningSession:
    concept_id: str
    concept_name: str
    question: str
    state: ConceptState
    phase: str = "question"
    analysis: Analysis | None = None
    diagnosed_misconception: str | None = None
    analysis_count: int = 0


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, LearningSession] = {}

    def add(self, session_id: str, session: LearningSession) -> None:
        self._sessions[session_id] = session

    def get(self, session_id: str) -> LearningSession | None:
        return self._sessions.get(session_id)

    def clear(self) -> None:
        self._sessions.clear()
