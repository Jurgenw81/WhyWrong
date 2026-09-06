import { ArrowRight, BrainCircuit, MessageCircleQuestion, ScanSearch, Sparkles } from "lucide-react";

const steps = [
  [MessageCircleQuestion, "Explain", "Answer in your own words—not a multiple-choice guess."],
  [ScanSearch, "Diagnose", "WhyWrong identifies the mental model behind the mistake."],
  [Sparkles, "Repair", "A targeted probe and short lesson fix the specific gap."],
];

export default function LandingPage({ concepts, onStart }) {
  return (
    <main className="landing">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">AI LEARNING DEBUGGER</span>
          <h1>Don’t just correct mistakes. <em>Understand them.</em></h1>
          <p>Learn neural networks from zero. WhyWrong teaches each idea, checks your explanation, and diagnoses why an answer is wrong before showing the fix.</p>
          <button className="primary-button hero-button" onClick={onStart}>Start learning <ArrowRight size={18} /></button>
          <span className="hero-note">12 beginner lessons · no prior AI knowledge required</span>
        </div>
        <div className="hero-visual" aria-label="WhyWrong diagnostic example">
          <div className="visual-orbit"><BrainCircuit size={38} /><span>YOUR ANSWER</span></div>
          <div className="visual-line" />
          <div className="visual-result"><span className="eyebrow">ROOT CAUSE</span><strong>Gradient ≠ weight update</strong><p>Ask one question to distinguish the misconception.</p></div>
        </div>
      </section>

      <section className="how-it-works">
        <span className="eyebrow">HOW IT WORKS</span>
        <h2>A tutor that asks why.</h2>
        <div className="step-cards">{steps.map(([Icon, title, text], index) => <article key={title}><span className="step-index">0{index + 1}</span><Icon size={21} /><h3>{title}</h3><p>{text}</p></article>)}</div>
      </section>

      <section className="course-preview">
        <div><span className="eyebrow">BEGINNER PATH</span><h2>Neural Networks from Zero</h2><p>See how the pieces connect—from a single neuron to training and generalization.</p></div>
        <div className="topic-cloud">{concepts.map((concept, index) => <span key={concept.id}><b>{String(index + 1).padStart(2, "0")}</b>{concept.name}</span>)}</div>
      </section>
    </main>
  );
}
