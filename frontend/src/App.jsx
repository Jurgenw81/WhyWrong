import { useEffect, useState } from "react";
import { Activity } from "lucide-react";
import { getConcepts, startSession, submitAnswer, submitProbe } from "./api";
import KnowledgeMap from "./components/KnowledgeMap";
import LearningPanel from "./components/LearningPanel";
import CurriculumRail from "./components/CurriculumRail";

export default function App() {
  const [session, setSession] = useState(null);
  const [result, setResult] = useState(null);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [concepts, setConcepts] = useState([]);
  const [conceptId, setConceptId] = useState("neural_networks");
  const [showLesson, setShowLesson] = useState(true);
  const [completed, setCompleted] = useState(() => new Set());

  async function begin(nextConceptId = conceptId) {
    setLoading(true);
    setError("");
    setResult(null);
    setAnswer("");
    try {
      setSession(await startSession(nextConceptId));
    } catch (err) {
      setError(`${err.message}. Is the FastAPI server running on port 8000?`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getConcepts().then(setConcepts).catch(() => {});
    begin("neural_networks");
  }, []);

  function chooseConcept(nextConceptId) {
    setConceptId(nextConceptId);
    setShowLesson(true);
    begin(nextConceptId);
  }

  async function handleAnswer(event) {
    event.preventDefault();
    if (!answer.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await submitAnswer(session.session_id, answer);
      setResult(data);
      setSession((current) => ({
        ...current,
        phase: data.next_action === "pass" ? "complete" : "probe",
        state: data.state,
      }));
      setAnswer("");
      if (data.next_action === "pass") setCompleted((current) => new Set([...current, conceptId]));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleProbe(choice) {
    setLoading(true);
    setError("");
    try {
      const data = await submitProbe(session.session_id, choice);
      setResult(data);
      setSession((current) => ({
        ...current,
        phase: data.next_action === "intervene" ? "lesson" : "probe",
        state: data.state,
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const phase = session?.phase || "loading";
  const mastery = session?.state?.mastery_probability ?? 0.35;
  const selectedConcept = concepts.find((item) => item.id === conceptId);
  const activeIndex = concepts.findIndex((item) => item.id === conceptId);
  const nextConcept = concepts[activeIndex + 1];

  return (
    <div className="app-shell">
      <header>
        <a className="brand" href="/">
          <span className="brand-mark">W?</span>
          <span>WhyWrong</span>
        </a>
        <div className="header-meta">
          <span><Activity size={14} /> Diagnostic engine live</span>
        </div>
      </header>

      <main>
        <div className="intro">
          <span className="eyebrow">AI LEARNING DEBUGGER</span>
          <p>Don’t just correct mistakes. Understand them.</p>
        </div>
        <div className="workspace">
          <CurriculumRail concepts={concepts} activeId={conceptId} completed={completed} onChoose={chooseConcept} />
          <KnowledgeMap phase={phase} mastery={mastery} conceptId={conceptId} />
          <LearningPanel
            session={session}
            result={result}
            answer={answer}
            setAnswer={setAnswer}
            loading={loading}
            error={error}
            onAnswer={handleAnswer}
            onProbe={handleProbe}
            onRestart={() => begin(conceptId)}
            concept={selectedConcept}
            showLesson={showLesson}
            onStartCheck={() => setShowLesson(false)}
            nextConcept={nextConcept}
            onNext={() => nextConcept && chooseConcept(nextConcept.id)}
          />
        </div>
      </main>

      <footer>
        <span>Prometheus Fall Classic · 2026</span>
        <span>Reasoning, not rote answers.</span>
      </footer>
    </div>
  );
}
