import { useMemo, useState } from "react";

const networkParts = [
  ["inputs", "Inputs", "The numbers the network receives: pixels, measurements, words, or other features."],
  ["hidden", "Hidden layer", "Neurons combine incoming values with learned weights to build a new representation."],
  ["activation", "Activation", "A nonlinear function lets stacked layers learn relationships more complex than one straight line."],
  ["output", "Output", "The final layer produces the prediction, such as a class score or numerical estimate."],
];

const loopParts = [
  ["layers_forward_pass", "Forward", "Use the current weights to turn an input into a prediction."],
  ["loss_functions", "Loss", "Compare that prediction with the target and produce an error signal."],
  ["backpropagation", "Backprop", "Apply the chain rule backward to find each parameter's contribution to the loss."],
  ["gradients", "Gradients", "Store local slope information for every trainable parameter."],
  ["optimizers", "Optimizer", "Use the gradients and an update rule to change the parameters."],
  ["learning_rate", "Update", "Scale the size of the parameter change, then repeat with another batch."],
];

const curveParts = [
  ["training", "Training loss", "Error on examples used to update the model. It can keep falling even after generalization worsens."],
  ["validation", "Validation loss", "Error on held-out examples. It estimates whether learning transfers to unseen data."],
  ["gap", "Generalization gap", "When validation loss rises while training loss falls, the model is beginning to overfit."],
];

function NetworkSvg({ selected }) {
  return <svg viewBox="0 0 520 250" role="img" aria-label="Inputs connect to a hidden layer, activations, and an output">
    <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" /></marker></defs>
    <g className="visual-edges"><path d="M82 55L218 48M82 55L218 125M82 125L218 48M82 125L218 125M82 195L218 125M82 195L218 202M238 48L372 85M238 125L372 85M238 125L372 165M238 202L372 165" /></g>
    <g className={`visual-nodes ${selected === "inputs" ? "active" : ""}`}><circle cx="72" cy="55" r="18"/><circle cx="72" cy="125" r="18"/><circle cx="72" cy="195" r="18"/></g>
    <g className={`visual-nodes ${selected === "hidden" ? "active" : ""}`}><circle cx="228" cy="48" r="20"/><circle cx="228" cy="125" r="20"/><circle cx="228" cy="202" r="20"/></g>
    <g className={`visual-nodes ${selected === "activation" ? "active" : ""}`}><circle cx="382" cy="85" r="22"/><circle cx="382" cy="165" r="22"/></g>
    <path className={`visual-arrow ${selected === "output" ? "active" : ""}`} d="M408 125H476" markerEnd="url(#arrow)" />
    <text x="72" y="232" textAnchor="middle">INPUTS</text><text x="228" y="232" textAnchor="middle">HIDDEN LAYER</text><text x="382" y="205" textAnchor="middle">ACTIVATIONS</text><text x="476" y="113" textAnchor="middle">OUTPUT</text>
  </svg>;
}

function LoopSvg({ selected }) {
  const steps = [["layers_forward_pass","FORWARD",70,55],["loss_functions","LOSS",260,55],["backpropagation","BACKPROP",450,55],["gradients","GRADIENTS",450,190],["optimizers","OPTIMIZER",260,190],["learning_rate","UPDATE",70,190]];
  return <svg viewBox="0 0 520 250" role="img" aria-label="Forward pass, loss, backpropagation, gradients, optimizer, and update form a loop">
    <path className="loop-path" d="M106 55H220M300 55H410M450 90V155M410 190H300M220 190H106M70 155V90" />
    {steps.map(([id,label,x,y]) => <g key={id} className={`loop-step ${selected === id ? "active" : ""}`}><circle cx={x} cy={y} r="34"/><text x={x} y={y+4} textAnchor="middle">{label}</text></g>)}
    <text className="loop-center" x="260" y="126" textAnchor="middle">ONE TRAINING STEP</text>
  </svg>;
}

function CurvesSvg({ selected }) {
  return <svg viewBox="0 0 520 250" role="img" aria-label="Training loss falls while validation loss eventually rises">
    <path className="chart-axis" d="M62 22V210H486"/><path className="chart-grid" d="M62 68H486M62 115H486M62 162H486"/>
    <path className={`chart-line training ${selected === "training" ? "active" : ""}`} d="M70 40C150 85 205 130 280 157S410 191 480 200"/>
    <path className={`chart-line validation ${selected === "validation" ? "active" : ""}`} d="M70 50C145 92 215 137 286 146S404 120 480 78"/>
    <path className={`overfit-line ${selected === "gap" ? "active" : ""}`} d="M302 25V210"/>
    <text x="370" y="64">VALIDATION</text><text x="382" y="197">TRAINING</text><text x="275" y="232" textAnchor="middle">EPOCHS</text><text className="overfit-label" x="312" y="39">OVERFITTING</text>
  </svg>;
}

export default function ConceptVisual({ conceptId }) {
  const type = ["loss_functions","gradients","backpropagation","optimizers","learning_rate"].includes(conceptId) ? "loop" : ["batches_epochs","data_splits","overfitting"].includes(conceptId) ? "curves" : "network";
  const parts = type === "loop" ? loopParts : type === "curves" ? curveParts : networkParts;
  const preferred = type === "loop" ? conceptId : type === "curves" ? (conceptId === "overfitting" ? "gap" : conceptId === "data_splits" ? "validation" : "training") : conceptId === "activation_functions" ? "activation" : conceptId === "neurons_weights_biases" ? "hidden" : "inputs";
  const [choice, setChoice] = useState(null);
  const selected = choice && parts.some(([id]) => id === choice) ? choice : preferred;
  const detail = useMemo(() => parts.find(([id]) => id === selected), [parts, selected]);

  return <div className="concept-visual">
    <div className="visual-header"><span>{type === "loop" ? "THE TRAINING LOOP" : type === "curves" ? "TRAINING VS. GENERALIZATION" : "FROM INPUT TO PREDICTION"}</span><small>SELECT A PART TO EXPLORE</small></div>
    {type === "loop" ? <LoopSvg selected={selected}/> : type === "curves" ? <CurvesSvg selected={selected}/> : <NetworkSvg selected={selected}/>}
    <div className="visual-controls">{parts.map(([id,label]) => <button key={id} className={selected === id ? "active" : ""} aria-pressed={selected === id} onClick={() => setChoice(id)}>{label}</button>)}</div>
    <div className="visual-detail" aria-live="polite"><strong>{detail[1]}</strong><span>{detail[2]}</span></div>
  </div>;
}
