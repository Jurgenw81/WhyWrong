from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.api.schemas import (
    AnalysisResponse,
    AnswerRequest,
    ConceptStateResponse,
    HealthResponse,
    HypothesisResponse,
    ProbeResponse,
    SessionResponse,
    StartSessionRequest,
)
from backend.api.store import LearningSession, SessionStore
from backend.diagnostic import DiagnosticEngine, MasteryEngine
from backend.diagnostic.models import Analysis, ConceptState, NextAction


CURRICULUM_PATH = (
    Path(__file__).resolve().parents[1] / "curriculum" / "neural_networks.json"
)


def load_concepts() -> dict[str, dict[str, object]]:
    curriculum = json.loads(CURRICULUM_PATH.read_text(encoding="utf-8"))
    return {concept["id"]: concept for concept in curriculum["concepts"]}


app = FastAPI(
    title="WhyWrong API",
    description="Diagnose the misconception behind a student's wrong answer.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
diagnostic_engine = DiagnosticEngine()
mastery_engine = MasteryEngine()
session_store = SessionStore()
concepts = load_concepts()


def get_session(session_id: str) -> LearningSession:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Learning session not found")
    return session


def serialize_state(state: ConceptState) -> ConceptStateResponse:
    return ConceptStateResponse(
        concept_id=state.concept_id,
        mastery_probability=state.mastery_probability,
        evidence_count=state.evidence_count,
        misconceptions=sorted(state.misconceptions),
    )


def serialize_analysis(
    session_id: str,
    session: LearningSession,
    analysis: Analysis,
    *,
    lesson: str | None = None,
    misconception_id: str | None = None,
) -> AnalysisResponse:
    probe = None
    if analysis.probe is not None:
        probe = ProbeResponse(
            id=analysis.probe.id,
            question=analysis.probe.question,
            choices=list(analysis.probe.choices),
        )
    return AnalysisResponse(
        session_id=session_id,
        correctness=analysis.correctness,
        reasoning_quality=analysis.reasoning_quality,
        next_action=analysis.next_action.value,
        hypotheses=[
            HypothesisResponse(
                id=item.id,
                label=item.label,
                probability=item.probability,
                evidence=item.evidence,
            )
            for item in analysis.hypotheses
        ],
        probe=probe,
        lesson=lesson,
        misconception_id=misconception_id,
        state=serialize_state(session.state),
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/api/sessions", response_model=SessionResponse, status_code=201)
async def start_session(request: StartSessionRequest) -> SessionResponse:
    concept = concepts.get(request.concept_id)
    if concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")

    session_id = str(uuid4())
    session = LearningSession(
        concept_id=request.concept_id,
        concept_name=str(concept["name"]),
        question=str(concept["question"]),
        state=ConceptState(request.concept_id),
    )
    session_store.add(session_id, session)
    return SessionResponse(
        session_id=session_id,
        concept_id=session.concept_id,
        concept_name=session.concept_name,
        question=session.question,
        phase="question",
        state=serialize_state(session.state),
    )


@app.post("/api/sessions/{session_id}/answer", response_model=AnalysisResponse)
async def analyze_answer(session_id: str, request: AnswerRequest) -> AnalysisResponse:
    session = get_session(session_id)
    if session.phase not in {"question", "lesson"}:
        raise HTTPException(status_code=409, detail="A diagnostic probe is pending")

    analysis = diagnostic_engine.analyze(request.answer)
    session.analysis = analysis
    if analysis.next_action is NextAction.PASS:
        mastery_engine.update(
            session.state,
            correct=True,
            misconception_id=session.diagnosed_misconception,
        )
        session.phase = "complete"
    else:
        session.phase = "probe"
    return serialize_analysis(session_id, session, analysis)


@app.post("/api/sessions/{session_id}/probe", response_model=AnalysisResponse)
async def answer_probe(session_id: str, request: AnswerRequest) -> AnalysisResponse:
    session = get_session(session_id)
    if session.phase != "probe" or session.analysis is None:
        raise HTTPException(status_code=409, detail="No diagnostic probe is pending")

    try:
        hypotheses, misconception_id, lesson = diagnostic_engine.apply_probe(
            session.analysis, request.answer
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    resolved = Analysis(
        correctness=session.analysis.correctness,
        reasoning_quality=session.analysis.reasoning_quality,
        hypotheses=hypotheses,
        next_action=NextAction.INTERVENE if misconception_id else NextAction.PROBE,
        probe=None if misconception_id else session.analysis.probe,
    )
    session.analysis = resolved
    if misconception_id:
        session.diagnosed_misconception = misconception_id
        mastery_engine.update(
            session.state, correct=False, misconception_id=misconception_id
        )
        session.phase = "lesson"

    return serialize_analysis(
        session_id,
        session,
        resolved,
        lesson=lesson,
        misconception_id=misconception_id,
    )


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def read_session(session_id: str) -> SessionResponse:
    session = get_session(session_id)
    return SessionResponse(
        session_id=session_id,
        concept_id=session.concept_id,
        concept_name=session.concept_name,
        question=session.question,
        phase=session.phase,
        state=serialize_state(session.state),
    )
