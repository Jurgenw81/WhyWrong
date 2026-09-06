function NetworkVisual({ conceptId }) {
  const active = conceptId === "activation_functions" ? "activation" : conceptId === "neurons_weights_biases" ? "neuron" : "flow";
  return <svg viewBox="0 0 520 280" role="img" aria-label="Inputs flow through weighted neurons and hidden layers to an output">
    <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" /></marker></defs>
    <g className="visual-edges"><path d="M82 70L218 62M82 70L218 140M82 140L218 62M82 140L218 140M82 210L218 140M82 210L218 218M238 62L372 100M238 140L372 100M238 140L372 182M238 218L372 182" /></g>
    <g className={active === "flow" ? "visual-nodes active" : "visual-nodes"}><circle cx="72" cy="70" r="18"/><circle cx="72" cy="140" r="18"/><circle cx="72" cy="210" r="18"/></g>
    <g className={active === "neuron" ? "visual-nodes active" : "visual-nodes"}><circle cx="228" cy="62" r="20"/><circle cx="228" cy="140" r="20"/><circle cx="228" cy="218" r="20"/></g>
    <g className={active === "activation" ? "visual-nodes active" : "visual-nodes"}><circle cx="382" cy="100" r="22"/><circle cx="382" cy="182" r="22"/></g>
    <path className="visual-arrow" d="M408 141H476" markerEnd="url(#arrow)" />
    <text x="72" y="252" textAnchor="middle">INPUTS</text><text x="228" y="252" textAnchor="middle">HIDDEN LAYER</text><text x="382" y="222" textAnchor="middle">ACTIVATIONS</text><text x="477" y="130" textAnchor="middle">OUTPUT</text>
  </svg>;
}

function TrainingLoopVisual({ conceptId }) {
  const steps = [
    ["layers_forward_pass", "FORWARD", 70, 62], ["loss_functions", "LOSS", 260, 62],
    ["backpropagation", "BACKPROP", 450, 62], ["gradients", "GRADIENTS", 450, 202],
    ["optimizers", "OPTIMIZER", 260, 202], ["learning_rate", "UPDATE", 70, 202],
  ];
  return <svg viewBox="0 0 520 280" role="img" aria-label="Training loop from forward pass to loss, backpropagation, gradients, optimizer, and weight update">
    <defs><marker id="loop-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" /></marker></defs>
    <path className="loop-path" d="M105 62H220M300 62H410M450 92V168M410 202H305M215 202H110M70 168V92" markerMid="url(#loop-arrow)" />
    {steps.map(([id, label, x, y]) => <g key={id} className={`loop-step ${conceptId === id ? "active" : ""}`}><circle cx={x} cy={y} r="34"/><text x={x} y={y + 4} textAnchor="middle">{label}</text></g>)}
    <text className="loop-center" x="260" y="137" textAnchor="middle">REPEAT OVER BATCHES</text>
  </svg>;
}

function CurvesVisual({ conceptId }) {
  return <svg viewBox="0 0 520 280" role="img" aria-label="Training loss falls while validation loss eventually rises, showing overfitting">
    <path className="chart-axis" d="M62 30V232H486" />
    <path className="chart-grid" d="M62 80H486M62 130H486M62 180H486" />
    <path className="chart-line training" d="M70 52C150 100 205 145 280 174S410 211 480 220" />
    <path className="chart-line validation" d="M70 62C145 105 215 154 286 163S404 133 480 91" />
    <path className="overfit-line" d="M302 36V232" />
    <text x="375" y="73">VALIDATION LOSS</text><text x="374" y="217">TRAINING LOSS</text>
    <text x="278" y="252" textAnchor="middle">TRAINING TIME / EPOCHS</text><text transform="translate(20 145) rotate(-90)" textAnchor="middle">LOSS</text>
    <text className="overfit-label" x="312" y="50">OVERFITTING BEGINS</text>
    {conceptId === "data_splits" && <text className="chart-callout" x="285" y="113">UNSEEN VALIDATION DATA REVEALS THE GAP</text>}
  </svg>;
}

export default function ConceptVisual({ conceptId }) {
  const trainingTopics = new Set(["loss_functions", "gradients", "backpropagation", "optimizers", "learning_rate"]);
  const curveTopics = new Set(["batches_epochs", "data_splits", "overfitting"]);
  return <div className="concept-visual">
    <div className="visual-title">{trainingTopics.has(conceptId) ? "THE TRAINING LOOP" : curveTopics.has(conceptId) ? "TRAINING VS. GENERALIZATION" : "FROM INPUT TO PREDICTION"}</div>
    {trainingTopics.has(conceptId) ? <TrainingLoopVisual conceptId={conceptId} /> : curveTopics.has(conceptId) ? <CurvesVisual conceptId={conceptId} /> : <NetworkVisual conceptId={conceptId} />}
  </div>;
}
