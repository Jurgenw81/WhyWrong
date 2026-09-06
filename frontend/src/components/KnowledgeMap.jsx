import { Check, CircleHelp, Search, TriangleAlert } from "lucide-react";

const defaultNodes = [
  { id: "derivatives", label: "Derivatives", x: 10, y: 20, state: "unknown" },
  { id: "chain", label: "Chain rule", x: 29, y: 55, state: "unknown" },
  { id: "graphs", label: "Computational graphs", x: 29, y: 10, state: "unknown" },
  { id: "gradients", label: "Gradients", x: 52, y: 34, state: "unknown" },
  { id: "backprop", label: "Backpropagation", x: 74, y: 34, state: "focus" },
  { id: "optimizer", label: "Optimizer updates", x: 91, y: 68, state: "unknown" },
];

const topicMaps = {
  neural_networks: ["Examples", "Inputs", "Layers", "Learned weights", "Neural network", "Outputs"],
  neurons_weights_biases: ["Features", "Inputs", "Multiplication", "Weighted sum", "Neuron", "Bias + activation"],
  layers_forward_pass: ["Input layer", "Early features", "Hidden layers", "Representations", "Forward pass", "Prediction"],
  activation_functions: ["Inputs", "Weighted sums", "Linear layers", "Nonlinearity", "Activation functions", "Expressive network"],
  loss_functions: ["Prediction", "Target", "Comparison", "Error signal", "Loss function", "Training objective"],
  gradients: ["Parameters", "Loss", "Sensitivity", "Local slope", "Gradient", "Update information"],
  optimizers: ["Loss", "Gradients", "Update rule", "Parameter state", "Optimizer", "New weights"],
  learning_rate: ["Loss", "Gradients", "Update direction", "Step size", "Learning rate", "Convergence"],
  batches_epochs: ["Dataset", "Examples", "Mini-batch", "Optimizer steps", "Epoch", "Training history"],
  data_splits: ["All examples", "Training set", "Validation set", "Model choices", "Test set", "Final estimate"],
  overfitting: ["Training data", "Training loss", "Model capacity", "Validation data", "Generalization", "Overfitting"],
};

function nodesFor(conceptId) {
  const labels = topicMaps[conceptId];
  if (!labels) return defaultNodes;
  return defaultNodes.map((node, index) => ({
    ...node,
    label: labels[index],
    id: index === 4 ? "backprop" : index === 5 ? "optimizer" : node.id,
  }));
}

function stateFor(node, phase) {
  if (node.id === "backprop") {
    if (phase === "complete") return "mastered";
    if (phase === "lesson") return "misconception";
    return "focus";
  }
  return node.state;
}

function assessmentStatus(phase, evidenceCount) {
  if (!evidenceCount && phase === "question") return "Not assessed";
  if (phase === "complete") return "Demonstrated";
  if (phase === "lesson") return "Misconception found";
  return "Assessment in progress";
}

function NodeIcon({ state }) {
  if (state === "mastered") return <Check size={15} strokeWidth={3} />;
  if (state === "misconception") return <TriangleAlert size={15} />;
  if (state === "focus") return <Search size={15} />;
  return <CircleHelp size={15} />;
}

export default function KnowledgeMap({ phase, evidenceCount, conceptId }) {
  const nodes = nodesFor(conceptId);
  return (
    <section className="map-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">KNOWLEDGE MRI</span>
          <h2>Current concept model</h2>
        </div>
        <div className="mastery-pill">{assessmentStatus(phase, evidenceCount)}</div>
      </div>

      <div className="graph" aria-label="Neural network knowledge map">
        <svg className="edges" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path d="M16 27 L31 55" />
          <path d="M38 18 L53 38" />
          <path d="M38 59 L53 42" />
          <path d="M60 40 L74 40" />
          <path d="M80 46 L89 67" />
        </svg>
        {nodes.map((node) => {
          const state = stateFor(node, phase);
          return (
            <div
              className={`concept-node ${state}`}
              key={node.id}
              style={{ left: `${node.x}%`, top: `${node.y}%` }}
            >
              <span className="node-icon"><NodeIcon state={state} /></span>
              <span>{node.label}</span>
            </div>
          );
        })}
      </div>

      <div className="legend">
        <span><i className="dot mastered" /> Demonstrated here</span>
        <span><i className="dot uncertain" /> Being assessed</span>
        <span><i className="dot unknown" /> Not assessed</span>
        <span><i className="dot misconception" /> Misconception</span>
      </div>
    </section>
  );
}
