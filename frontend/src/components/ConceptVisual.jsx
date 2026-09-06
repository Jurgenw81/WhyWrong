import { useState } from "react";

const VISUALS = {
  neural_networks: {
    title: "A NETWORK IS A TRAINABLE PIPELINE",
    options: [
      ["input", "Input", "Raw information enters the network as numbers."],
      ["layers", "Layers", "Connected neurons transform those numbers using learned weights."],
      ["output", "Output", "The final numbers become a prediction."],
    ],
  },
  neurons_weights_biases: {
    title: "INSIDE ONE NEURON",
    options: [
      ["weights", "Weights", "Each input is multiplied by a learned weight that controls its influence."],
      ["bias", "Bias", "A learned offset shifts the neuron's response independently of its inputs."],
      ["sum", "Weighted sum", "The neuron adds the weighted inputs and bias before activation."],
    ],
  },
  layers_forward_pass: {
    title: "FEATURES BECOME MORE ABSTRACT",
    options: [
      ["early", "Early layer", "Early layers detect simple patterns such as edges."],
      ["middle", "Middle layer", "Middle layers combine simple patterns into shapes or parts."],
      ["late", "Late layer", "Late layers combine those parts into task-relevant concepts."],
    ],
  },
  activation_functions: {
    title: "RELU BENDS A LINEAR SIGNAL",
    options: [
      ["negative", "Negative input", "ReLU maps negative values to zero."],
      ["positive", "Positive input", "ReLU keeps positive values, producing a nonlinear bend at zero."],
      ["stacked", "Why it matters", "Nonlinearity prevents many layers from collapsing into one linear transformation."],
    ],
  },
  loss_functions: {
    title: "LOSS MEASURES THE PREDICTION GAP",
    options: [
      ["target", "Target", "The correct value provides the reference for this training example."],
      ["prediction", "Prediction", "The network's current output may be close to or far from the target."],
      ["loss", "Loss", "The loss function converts that mismatch into a number to minimize."],
    ],
  },
  gradients: {
    title: "A GRADIENT IS THE LOCAL SLOPE",
    options: [
      ["point", "Current weight", "This point is the parameter's current value on the loss curve."],
      ["slope", "Gradient", "The tangent slope says how loss changes for a tiny change in the weight."],
      ["direction", "Descent direction", "To reduce loss, gradient descent usually moves opposite the gradient."],
    ],
  },
  backpropagation: {
    title: "CREDIT ASSIGNMENT MOVES BACKWARD",
    options: [
      ["loss", "Start at loss", "Backpropagation begins with how the output affected the loss."],
      ["chain", "Apply chain rule", "Local derivatives are multiplied backward through connected operations."],
      ["parameters", "Parameter gradients", "Every weight receives a gradient describing its contribution—not a new value."],
    ],
  },
  optimizers: {
    title: "THE OPTIMIZER CHANGES THE PARAMETERS",
    options: [
      ["gradient", "Read gradient", "The optimizer receives gradients already computed by backpropagation."],
      ["rule", "Apply update rule", "SGD, momentum, and Adam transform gradient information differently."],
      ["weight", "New weight", "Only this step writes the updated parameter value."],
    ],
  },
  learning_rate: {
    title: "STEP SIZE CHANGES THE PATH",
    options: [
      ["small", "Too small", "Tiny steps are stable but may need far too many updates."],
      ["balanced", "Balanced", "Moderate steps can approach the minimum efficiently."],
      ["large", "Too large", "Oversized steps can jump across the minimum and diverge."],
    ],
  },
  batches_epochs: {
    title: "BATCHES MAKE UP ONE EPOCH",
    options: [
      ["example", "Example", "One row represents one training example."],
      ["batch", "Batch", "A batch is a subset processed before an optimizer update."],
      ["epoch", "Epoch", "One epoch is complete after every training example has been used once."],
    ],
  },
  data_splits: {
    title: "THREE SPLITS, THREE DIFFERENT JOBS",
    options: [
      ["train", "Train", "Training examples directly influence the learned weights."],
      ["validation", "Validation", "Validation results guide model choices without directly updating weights."],
      ["test", "Test", "The untouched test set provides a final estimate after decisions are finished."],
    ],
  },
  overfitting: {
    title: "THE GENERALIZATION GAP OPENS",
    options: [
      ["training", "Training loss", "Training error can keep falling as the model memorizes details."],
      ["validation", "Validation loss", "Held-out error eventually rises when learned details stop generalizing."],
      ["gap", "Overfitting gap", "The growing distance between the curves is the warning signal."],
    ],
  },
};

function Network({ selected }) {
  return <svg viewBox="0 0 520 230"><g className={`diagram-zone ${selected === "input" ? "active" : ""}`}><rect x="24" y="45" width="105" height="140" rx="16"/><text x="76" y="107">PIXELS</text><text x="76" y="127">INPUT</text></g><path className="diagram-arrow" d="M145 115H198"/><g className={`diagram-zone ${selected === "layers" ? "active" : ""}`}><circle cx="230" cy="65" r="18"/><circle cx="230" cy="115" r="18"/><circle cx="230" cy="165" r="18"/><circle cx="310" cy="85" r="18"/><circle cx="310" cy="145" r="18"/><path d="M248 65L292 85M248 65L292 145M248 115L292 85M248 115L292 145M248 165L292 85M248 165L292 145"/></g><path className="diagram-arrow" d="M342 115H390"/><g className={`diagram-zone ${selected === "output" ? "active" : ""}`}><rect x="405" y="70" width="90" height="90" rx="16"/><text x="450" y="108">DIGIT</text><text x="450" y="128">“7”</text></g></svg>;
}

function Neuron({ selected }) {
  return <svg viewBox="0 0 520 230"><g className={`diagram-zone ${selected === "weights" ? "active" : ""}`}><text x="32" y="60">x₁ × w₁</text><text x="32" y="115">x₂ × w₂</text><text x="32" y="170">x₃ × w₃</text><path d="M110 55L210 105M110 110L210 110M110 165L210 115"/></g><g className={`diagram-zone ${selected === "sum" ? "active" : ""}`}><circle cx="260" cy="110" r="52"/><text x="260" y="106">Σ</text><text x="260" y="126">WEIGHTED SUM</text></g><g className={`diagram-zone ${selected === "bias" ? "active" : ""}`}><rect x="218" y="184" width="84" height="30" rx="9"/><text x="260" y="203">+ BIAS</text><path d="M260 184V164"/></g><path className="diagram-arrow" d="M314 110H470"/><text x="408" y="98">TO ACTIVATION</text></svg>;
}

function Layers({ selected }) {
  const items = [["early","EDGES","╱  ─  ╲",38],["middle","SHAPES","△  ○  □",200],["late","OBJECT","CAT",362]];
  return <svg viewBox="0 0 520 230">{items.map(([id,label,value,x],i)=><g key={id} className={`diagram-zone ${selected === id ? "active" : ""}`}><rect x={x} y="58" width="120" height="110" rx="16"/><text x={x+60} y="87">{label}</text><text className="diagram-big" x={x+60} y="130">{value}</text>{i<2&&<path className="diagram-arrow" d={`M${x+126} 113H${x+154}`}/>}</g>)}</svg>;
}

function Relu({ selected }) {
  return <svg viewBox="0 0 520 230"><path className="chart-axis" d="M45 185H480M250 205V25"/><path className={`relu-negative ${selected === "negative" ? "active" : ""}`} d="M60 185H250"/><path className={`relu-positive ${selected === "positive" ? "active" : ""}`} d="M250 185L455 42"/><circle className="bend-point" cx="250" cy="185" r="6"/><text x="460" y="207">INPUT</text><text x="272" y="35">OUTPUT</text><text x="60" y="173">ZERO</text><text className={selected === "stacked" ? "active-text" : ""} x="345" y="92">NONLINEAR BEND</text></svg>;
}

function Loss({ selected }) {
  return <svg viewBox="0 0 520 230"><g className={`diagram-zone ${selected === "target" ? "active" : ""}`}><rect x="45" y="52" width="120" height="126" rx="16"/><text x="105" y="88">TARGET</text><text className="diagram-big" x="105" y="137">1.0</text></g><g className={`diagram-zone ${selected === "prediction" ? "active" : ""}`}><rect x="200" y="52" width="120" height="126" rx="16"/><text x="260" y="88">PREDICTION</text><text className="diagram-big" x="260" y="137">0.3</text></g><path className="diagram-arrow" d="M330 115H377"/><g className={`diagram-zone ${selected === "loss" ? "active" : ""}`}><circle cx="435" cy="115" r="54"/><text x="435" y="108">LOSS</text><text className="diagram-big" x="435" y="137">0.7</text></g></svg>;
}

function Gradient({ selected }) {
  return <svg viewBox="0 0 520 230"><path className="chart-axis" d="M48 20V195H485"/><path className="loss-curve" d="M70 48C160 55 170 175 275 174S365 75 470 45"/><circle className={selected === "point" ? "active-dot" : ""} cx="178" cy="135" r="7"/><path className={`tangent ${selected === "slope" ? "active" : ""}`} d="M112 78L244 190"/><path className={`descent ${selected === "direction" ? "active" : ""}`} d="M178 135L235 165"/><text x="72" y="36">LOSS</text><text x="410" y="215">WEIGHT VALUE</text><text x="118" y="70">GRADIENT</text><text x="230" y="153">MOVE DOWNHILL</text></svg>;
}

function Backprop({ selected }) {
  return <svg viewBox="0 0 520 230"><path className="forward-line" d="M55 80H465"/><path className="backward-line" d="M465 150H55"/>{[["parameters","WEIGHTS",65],["chain","LAYER 1",175],["chain","LAYER 2",285],["loss","LOSS",425]].map(([id,label,x])=><g key={label} className={`diagram-zone ${selected === id ? "active" : ""}`}><circle cx={x} cy="115" r="36"/><text x={x} y="119">{label}</text></g>)}<text x="60" y="55">FORWARD: VALUES →</text><text x="300" y="184">← BACKWARD: CHAIN RULE × LOCAL DERIVATIVES</text></svg>;
}

function Optimizer({ selected }) {
  return <svg viewBox="0 0 520 230"><g className={`diagram-zone ${selected === "gradient" ? "active" : ""}`}><rect x="35" y="70" width="115" height="90" rx="16"/><text x="92" y="105">GRADIENT</text><text className="diagram-big" x="92" y="135">+0.4</text></g><path className="diagram-arrow" d="M165 115H205"/><g className={`diagram-zone ${selected === "rule" ? "active" : ""}`}><rect x="220" y="55" width="120" height="120" rx="60"/><text x="280" y="108">ADAM / SGD</text><text x="280" y="130">UPDATE RULE</text></g><path className="diagram-arrow" d="M355 115H392"/><g className={`diagram-zone ${selected === "weight" ? "active" : ""}`}><rect x="407" y="70" width="80" height="90" rx="16"/><text x="447" y="103">WEIGHT</text><text x="447" y="126">1.0 → 0.96</text></g></svg>;
}

function LearningRate({ selected }) {
  const paths={small:"M70 70L115 88L155 105L190 120L220 132",balanced:"M70 115L165 155L255 175",large:"M70 165L300 65L190 190L430 48"};
  return <svg viewBox="0 0 520 230"><path className="loss-bowl" d="M45 30C135 35 150 195 260 195S380 35 475 30"/><circle cx="260" cy="195" r="6"/><text x="260" y="218" textAnchor="middle">LOW LOSS</text>{Object.entries(paths).map(([id,d])=><path key={id} className={`rate-path ${id} ${selected === id ? "active" : ""}`} d={d}/>)}</svg>;
}

function Batches({ selected }) {
  return <svg viewBox="0 0 520 230">{Array.from({length:24},(_,i)=>{const row=Math.floor(i/8),col=i%8;const inBatch=i<8;return <rect key={i} className={`data-cell ${selected === "example"&&i===2||selected === "batch"&&inBatch||selected === "epoch"?"active":""}`} x={42+col*55} y={48+row*52} width="38" height="32" rx="6"/>})}<text x="42" y="31">24 TRAINING EXAMPLES</text><path className="epoch-bracket" d="M32 39V195H493V39"/><text x="260" y="218" textAnchor="middle">ONE EPOCH = ALL THREE BATCHES</text></svg>;
}

function Splits({ selected }) {
  const items=[["train","TRAIN","70%",40,285],["validation","VALIDATE","15%",335,65],["test","TEST","15%",410,65]];
  return <svg viewBox="0 0 520 230"><text x="40" y="45">ONE DATASET, SPLIT BEFORE TRAINING</text>{items.map(([id,label,pct,x,w])=><g key={id} className={`split ${selected === id ? "active" : ""}`}><rect x={x} y="80" width={w} height="85" rx="10"/><text x={x+w/2} y="112" textAnchor="middle">{label}</text><text className="diagram-big" x={x+w/2} y="143" textAnchor="middle">{pct}</text></g>)}</svg>;
}

function Overfit({ selected }) {
  return <svg viewBox="0 0 520 230"><path className="chart-axis" d="M50 20V195H485"/><path className={`chart-line training ${selected === "training" ? "active" : ""}`} d="M65 42C155 87 210 135 300 165S415 185 475 190"/><path className={`chart-line validation ${selected === "validation" ? "active" : ""}`} d="M65 52C150 95 220 142 295 146S405 112 475 72"/><path className={`overfit-line ${selected === "gap" ? "active" : ""}`} d="M302 25V195"/><text x="374" y="61">VALIDATION</text><text x="390" y="184">TRAINING</text><text className="overfit-label" x="313" y="39">GAP OPENS</text></svg>;
}

const DIAGRAMS={neural_networks:Network,neurons_weights_biases:Neuron,layers_forward_pass:Layers,activation_functions:Relu,loss_functions:Loss,gradients:Gradient,backpropagation:Backprop,optimizers:Optimizer,learning_rate:LearningRate,batches_epochs:Batches,data_splits:Splits,overfitting:Overfit};

export default function ConceptVisual({ conceptId }) {
  const visual=VISUALS[conceptId]||VISUALS.neural_networks;
  const [choices,setChoices]=useState({});
  const selected=choices[conceptId]||visual.options[0][0];
  const Diagram=DIAGRAMS[conceptId]||Network;
  const detail=visual.options.find(([id])=>id===selected);
  return <div className="concept-visual">
    <div className="visual-header"><span>{visual.title}</span><small>SELECT A PART</small></div>
    <Diagram selected={selected}/>
    <div className="visual-controls">{visual.options.map(([id,label])=><button key={id} className={selected===id?"active":""} aria-pressed={selected===id} onClick={()=>setChoices(current=>({...current,[conceptId]:id}))}>{label}</button>)}</div>
    <div className="visual-detail" aria-live="polite"><strong>{detail[1]}</strong><span>{detail[2]}</span></div>
  </div>;
}
