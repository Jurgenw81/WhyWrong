from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.schemas import (
    AnalysisResponse,
    AnswerRequest,
    ConceptStateResponse,
    ConceptResponse,
    HealthResponse,
    HypothesisResponse,
    ProbeResponse,
    SessionResponse,
    StartSessionRequest,
)
from backend.api.rate_limit import SlidingWindowRateLimiter
from backend.api.store import LearningSession, SessionStore
from backend.diagnostic import DiagnosticEngine, MasteryEngine
from backend.diagnostic.concept_engine import engine_for
from backend.diagnostic.llm_classifier import OpenAIAnswerClassifier
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
llm_classifier = OpenAIAnswerClassifier.from_environment()
mastery_engine = MasteryEngine()
session_store = SessionStore()
analysis_limiter = SlidingWindowRateLimiter(
    limit=int(os.getenv("WHYWRONG_RATE_LIMIT", "10")),
    window_seconds=int(os.getenv("WHYWRONG_RATE_WINDOW_SECONDS", "60")),
)
max_session_analyses = int(os.getenv("WHYWRONG_MAX_SESSION_ANALYSES", "3"))
concepts = load_concepts()


@app.get("/api/concepts", response_model=list[ConceptResponse])
async def list_concepts() -> list[ConceptResponse]:
    return [
        ConceptResponse(
            id=str(item["id"]),
            name=str(item["name"]),
            question=str(item["question"]),
            prerequisites=[str(value) for value in item.get("prerequisites", [])],
            stage=str(item.get("stage", "NEURAL NETWORKS")),
            summary=str(item.get("summary", "")),
            explanation=str(item.get("explanation", "")),
            example=str(item.get("example", "")),
            connection=str(item.get("connection", "")),
        )
        for item in concepts.values()
    ]


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
        analysis_source=analysis.source,
        state=serialize_state(session.state),
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        classifier="openai" if llm_classifier else "deterministic",
        model=llm_classifier.model if llm_classifier else None,
    )


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
        diagnostic_engine=engine_for(request.concept_id),
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
async def analyze_answer(
    session_id: str, payload: AnswerRequest, request: Request
) -> AnalysisResponse:
    session = get_session(session_id)
    if session.phase not in {"question", "lesson"}:
        raise HTTPException(status_code=409, detail="A diagnostic probe is pending")
    if session.analysis_count >= max_session_analyses:
        raise HTTPException(
            status_code=429,
            detail="This learning session has reached its analysis limit.",
        )

    session_engine = session.diagnostic_engine or diagnostic_engine
    use_llm = llm_classifier is not None
    if use_llm:
        client_key = request.client.host if request.client else "unknown"
        allowed, retry_after = analysis_limiter.allow(client_key)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Too many AI analyses. Retry in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )
    session.analysis_count += 1

    if use_llm:
        try:
            analysis = await llm_classifier.analyze(payload.answer, session_engine)
        except Exception:
            logging.getLogger(__name__).exception(
                "Structured LLM classification failed; using deterministic fallback"
            )
            fallback = session_engine.analyze(payload.answer)
            analysis = Analysis(
                correctness=fallback.correctness,
                reasoning_quality=fallback.reasoning_quality,
                hypotheses=fallback.hypotheses,
                next_action=fallback.next_action,
                probe=fallback.probe,
                source="deterministic:fallback",
            )
    else:
        analysis = session_engine.analyze(payload.answer)
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
        session_engine = session.diagnostic_engine or diagnostic_engine
        hypotheses, misconception_id, lesson = session_engine.apply_probe(
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
        source=session.analysis.source,
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


# In production the Vite build is served by FastAPI, keeping the browser and
# API on one origin. The directory is absent during backend-only development.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
