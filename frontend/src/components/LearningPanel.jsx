import { ArrowRight, BrainCircuit, CheckCircle2, Lightbulb, Link2, LoaderCircle, RotateCcw, Sparkles } from "lucide-react";

function Hypotheses({ items, source }) {
  if (!items?.length) return null;
  return (
    <div className="hypotheses">
      <div className="hypothesis-heading">
        <span className="eyebrow">WORKING HYPOTHESES</span>
        {source?.startsWith("openai:") && <span className="ai-badge">STRUCTURED AI</span>}
      </div>
      {items.map((item) => (
        <div className="hypothesis" key={item.id}>
          <div className="hypothesis-line">
            <span>{item.label}</span>
            <strong>{Math.round(item.probability * 100)}%</strong>
          </div>
          <div className="probability-track">
            <i style={{ width: `${item.probability * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function LearningPanel({
  session,
  result,
  answer,
  setAnswer,
  loading,
  error,
  onAnswer,
  onProbe,
  onRestart,
  concept,
  showLesson,
  onStartCheck,
  nextConcept,
  onNext,
  lessonNumber,
  lessonTotal,
}) {
  const phase = session?.phase || "loading";

  return (
    <section className="learning-panel">
      <div className="lesson-progress">
        <div className="concept-kicker">
          <BrainCircuit size={17} /> {concept?.stage || "NEURAL NETWORKS"} · LESSON {lessonNumber || 1} OF {lessonTotal || 1}
        </div>
        <div className="lesson-progress-track"><i style={{ width: `${((lessonNumber || 1) / (lessonTotal || 1)) * 100}%` }} /></div>
      </div>

      {phase === "loading" && (
        <div className="loading-state"><LoaderCircle className="spin" /> Calibrating diagnostic…</div>
      )}

      {phase !== "loading" && showLesson && concept && (
        <div className="lesson-card">
          <div className="step-label">LEARN · THEN EXPLAIN</div>
          <h1>{concept.name}</h1>
          <p className="lesson-summary">{concept.summary}</p>
          <p className="lesson-explanation">{concept.explanation}</p>
          <div className="lesson-note"><Lightbulb size={17} /><div><span>EXAMPLE</span>{concept.example}</div></div>
          <div className="lesson-note connection"><Link2 size={17} /><div><span>HOW IT CONNECTS</span>{concept.connection}</div></div>
          <button className="primary-button" onClick={onStartCheck}>Check my understanding <ArrowRight size={18} /></button>
        </div>
      )}

      {!showLesson && (phase === "question" || phase === "probe") && session && (
        <>
          <div className="step-label">
            {phase === "question" ? "01 · CONCEPT CHECK" : "02 · DIAGNOSTIC PROBE"}
          </div>
          <h1>{phase === "question" ? session.question : result.probe.question}</h1>
          {phase === "question" ? (
            <form onSubmit={onAnswer}>
              <textarea
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="Explain it in your own words…"
                autoFocus
              />
              <button className="primary-button" disabled={loading || !answer.trim()}>
                {loading ? <LoaderCircle className="spin" size={18} /> : <>Analyze reasoning <ArrowRight size={18} /></>}
              </button>
            </form>
          ) : (
            <div className="choice-grid">
              {result.probe.choices.map((choice) => (
                <button key={choice} onClick={() => onProbe(choice)} disabled={loading}>
                  {choice}
                </button>
              ))}
            </div>
          )}
          <Hypotheses items={result?.hypotheses} source={result?.analysis_source} />
        </>
      )}

      {phase === "lesson" && (
        <>
          <div className="step-label warning">03 · ROOT CAUSE FOUND</div>
          <div className="diagnosis-title">
            <Sparkles size={22} />
            <h1>{result.hypotheses[0].label}</h1>
          </div>
          <Hypotheses items={result.hypotheses} source={result.analysis_source} />
          <div className="micro-lesson">
            <span className="eyebrow">TARGETED REPAIR</span>
            <p>{result.lesson}</p>
          </div>
          <form onSubmit={onAnswer}>
            <label htmlFor="retry">Now explain the distinction in your own words.</label>
            <textarea
              id="retry"
              value={answer}
              onChange={(event) => setAnswer(event.target.value)}
              placeholder="Backpropagation computes…"
              autoFocus
            />
            <button className="primary-button" disabled={loading || !answer.trim()}>
              Retry concept <ArrowRight size={18} />
            </button>
          </form>
        </>
      )}

      {phase === "complete" && (
        <div className="success-state">
          <CheckCircle2 size={44} />
          <span className="eyebrow">MENTAL MODEL REPAIRED</span>
          <h1>You found the boundary.</h1>
          <p>Your explanation now separates the mechanism from the misconception.</p>
          <button className="secondary-button" onClick={onRestart}>
            <RotateCcw size={17} /> Run demo again
          </button>
          {nextConcept && <button className="primary-button" onClick={onNext}>Next: {nextConcept.name} <ArrowRight size={17} /></button>}
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
    </section>
  );
}
