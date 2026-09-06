from __future__ import annotations

from dataclasses import dataclass

from .engine import DiagnosticEngine
from .models import Analysis, Hypothesis, NextAction, Probe
from .probes import update_beliefs


@dataclass(frozen=True)
class ConceptDiagnostic:
    correct_terms: tuple[tuple[str, ...], ...]
    hypotheses: tuple[tuple[str, str, tuple[str, ...]], ...]
    probe: Probe
    lessons: dict[str, str]


DIAGNOSTICS = {
    "activation_functions": ConceptDiagnostic(
        correct_terms=(("nonlinear", "linear"), ("non-linearity", "linear")),
        hypotheses=(
            ("activation_adds_weights", "Activation adds trainable weights", ("weight", "parameter")),
            ("activation_is_only_threshold", "Activations are only thresholds", ("threshold", "on or off", "binary")),
        ),
        probe=Probe(
            "linear_stack",
            "If every activation is removed, can many linear layers represent more than one linear transformation?",
            ("Yes", "No", "Not sure"),
            {
                "activation_adds_weights": {"Yes": .75, "No": .15, "Not sure": .10},
                "activation_is_only_threshold": {"Yes": .55, "No": .25, "Not sure": .20},
            },
        ),
        lessons={
            "activation_adds_weights": "Activations do not add trainable weights. Their nonlinearity prevents stacked layers from collapsing into one linear map.",
            "activation_is_only_threshold": "Modern activations need not be binary thresholds. ReLU, GELU, and sigmoid introduce nonlinear behavior in different ways.",
        },
    ),
    "learning_rate": ConceptDiagnostic(
        correct_terms=(("scale", "update"), ("step", "overshoot"), ("large", "diverge")),
        hypotheses=(
            ("learning_rate_changes_direction", "Learning rate chooses update direction", ("direction", "which way")),
            ("higher_is_always_faster", "A higher learning rate is always better", ("higher", "faster", "bigger")),
        ),
        probe=Probe(
            "same_gradient",
            "With the same gradient, does changing only the learning rate change the update direction?",
            ("Yes", "No", "Not sure"),
            {
                "learning_rate_changes_direction": {"Yes": .88, "No": .06, "Not sure": .06},
                "higher_is_always_faster": {"Yes": .25, "No": .60, "Not sure": .15},
            },
        ),
        lessons={
            "learning_rate_changes_direction": "The gradient and optimizer determine direction; the learning rate primarily scales the step size.",
            "higher_is_always_faster": "Larger steps can overshoot good solutions or diverge. Training speed depends on making stable progress, not maximizing the step size.",
        },
    ),
    "overfitting": ConceptDiagnostic(
        correct_terms=(("training", "generalize"), ("noise", "validation"), ("unseen", "training")),
        hypotheses=(
            ("training_loss_proves_generalization", "Low training loss proves generalization", ("training loss", "accurate", "good model")),
            ("more_training_always_helps", "More training always improves the model", ("more training", "longer", "more epochs")),
        ),
        probe=Probe(
            "validation_gap",
            "If training loss keeps falling while validation loss rises, is generalization improving?",
            ("Yes", "No", "Not sure"),
            {
                "training_loss_proves_generalization": {"Yes": .85, "No": .08, "Not sure": .07},
                "more_training_always_helps": {"Yes": .35, "No": .55, "Not sure": .10},
            },
        ),
        lessons={
            "training_loss_proves_generalization": "Training fit and generalization are different measurements. Validation data estimates performance on examples the model did not optimize against.",
            "more_training_always_helps": "After a point, extra epochs can fit training-specific noise. A widening validation gap is evidence that more training is hurting generalization.",
        },
    ),
}


def _basic_diagnostic(
    correct_terms, first, second, probe_question, first_lesson, second_lesson
):
    first_id, first_label, first_cues = first
    second_id, second_label, second_cues = second
    return ConceptDiagnostic(
        correct_terms=correct_terms,
        hypotheses=(first, second),
        probe=Probe(
            f"{first_id}_check",
            probe_question,
            ("Yes", "No", "Not sure"),
            {
                first_id: {"Yes": .84, "No": .08, "Not sure": .08},
                second_id: {"Yes": .12, "No": .76, "Not sure": .12},
            },
        ),
        lessons={first_id: first_lesson, second_id: second_lesson},
    )


DIAGNOSTICS.update(
    {
        "neural_networks": _basic_diagnostic(
            (("input", "output", "weight"), ("layer", "training", "weight")),
            ("fixed_program", "A neural network follows fixed hand-written rules", ("program", "fixed", "rules")),
            ("training_stores_answers", "Training stores every answer", ("memorize", "store", "database")),
            "Does training normally change learned weights inside the network?",
            "A neural network is not a fixed list of hand-written decisions. Training adjusts numerical weights that shape its input-to-output function.",
            "Networks can memorize, but their purpose is to learn reusable patterns in weights—not store a lookup table of every answer.",
        ),
        "neurons_weights_biases": _basic_diagnostic(
            (("weight", "bias", "shift"), ("weight", "input", "baseline")),
            ("weight_is_input", "A weight is the input value", ("input value", "data itself", "feature itself")),
            ("bias_is_error", "A bias is prediction error", ("error", "mistake", "loss")),
            "Can changing a weight alter how strongly one input affects a neuron?",
            "Inputs are data; weights are learned multipliers controlling how strongly those inputs influence the neuron.",
            "A bias is a learned offset in the neuron's calculation. It is not the model's prediction error or statistical unfairness.",
        ),
        "layers_forward_pass": _basic_diagnostic(
            (("input", "output", "layer"), ("transform", "layer", "prediction")),
            ("forward_updates_weights", "The forward pass updates weights", ("update", "change weights", "learns")),
            ("layers_repeat_inputs", "Every layer sees only the raw input", ("raw input", "same input", "repeat")),
            "Does a normal forward pass change model weights by itself?",
            "The forward pass calculates a prediction with the current weights. Learning happens only after loss, gradients, and an optimizer update.",
            "Hidden layers consume representations from earlier layers, letting later layers combine simpler features into richer ones.",
        ),
        "loss_functions": _basic_diagnostic(
            (("compare", "prediction", "target"), ("error", "objective", "update")),
            ("loss_updates_weights", "The loss function updates weights", ("update", "changes weights", "trains")),
            ("loss_equals_accuracy", "Loss and accuracy are the same metric", ("accuracy", "percent correct", "same")),
            "After loss is calculated, have the weights necessarily changed?",
            "Loss measures the objective. Backpropagation and the optimizer are separate steps that turn that signal into parameter changes.",
            "Accuracy counts correct decisions; loss measures graded prediction quality and supplies a differentiable training signal.",
        ),
        "gradients": _basic_diagnostic(
            (("slope", "loss", "parameter"), ("direction", "sensitivity", "loss")),
            ("gradient_is_update", "A gradient is the parameter update", ("update", "new weight", "amount changes")),
            ("gradient_is_error", "A gradient is the prediction error", ("error value", "wrong prediction", "loss itself")),
            "Can an optimizer scale or transform a gradient before updating a weight?",
            "A gradient is local slope information. The optimizer converts it into an update using the learning rate and its update rule.",
            "Loss measures prediction error; a gradient measures how that loss changes with respect to a particular parameter.",
        ),
        "optimizers": _basic_diagnostic(
            (("gradient", "update", "weight"), ("parameter", "learning rate", "change")),
            ("optimizer_computes_loss", "The optimizer computes the loss", ("computes loss", "compares target", "error")),
            ("optimizer_is_backprop", "The optimizer and backpropagation are the same step", ("same", "backprop", "backward")),
            "Can optimizer.step() change weights after gradients have already been computed?",
            "The forward computation and loss function produce the loss. The optimizer's job is to apply parameter updates.",
            "Backpropagation computes gradients; the optimizer consumes them and changes parameters. They are connected but separate.",
        ),
        "batches_epochs": _basic_diagnostic(
            (("batch", "epoch", "update"), ("whole dataset", "batch", "pass")),
            ("batch_is_epoch", "A batch and an epoch are the same", ("same", "entire dataset", "one batch")),
            ("epoch_means_new_data", "Every epoch uses brand-new data", ("new data", "new examples", "different dataset")),
            "If a dataset contains ten batches, is one batch equal to one epoch?",
            "A batch is one subset used for a training step; an epoch covers the complete training set, usually across many batches.",
            "Epochs normally revisit the training set in a new order. Repetition does not automatically create new examples.",
        ),
        "data_splits": _basic_diagnostic(
            (("training", "validation", "test"), ("tune", "final", "unseen")),
            ("all_data_for_training", "All available data should train the weights", ("all data", "train everything", "waste data")),
            ("validation_equals_test", "Validation and test sets have the same role", ("same", "both evaluate", "no difference")),
            "Should test examples influence repeated model-selection decisions?",
            "Holding data back is what lets us measure behavior beyond the examples that directly shaped the model.",
            "Validation guides choices during development; the test set is reserved for a final, less-biased estimate.",
        ),
    }
)


class ConceptDiagnosticEngine:
    def __init__(self, concept_id: str, diagnostic: ConceptDiagnostic) -> None:
        self.concept_id = concept_id
        self.diagnostic = diagnostic

    def analyze(self, answer: str) -> Analysis:
        text = " ".join(answer.lower().split())
        if any(all(term in text for term in group) for group in self.diagnostic.correct_terms):
            return Analysis(.93, .86, (), NextAction.PASS, source="deterministic")

        scores = []
        for hypothesis_id, label, cues in self.diagnostic.hypotheses:
            score = .72 if any(cue in text for cue in cues) else .45
            scores.append((hypothesis_id, label, score))
        if len(text.split()) < 4:
            scores = [(item[0], item[1], .5) for item in scores]
        total = sum(item[2] for item in scores)
        hypotheses = tuple(
            Hypothesis(item[0], item[1], round(item[2] / total, 4), "The wording leaves this mental model plausible.")
            for item in sorted(scores, key=lambda value: value[2], reverse=True)
        )
        return Analysis(.3, .5, hypotheses, NextAction.PROBE, self.diagnostic.probe)

    def from_classification(self, *, correctness, reasoning_quality, probabilities, evidence=None, source):
        if correctness >= .82:
            return Analysis(correctness, reasoning_quality, (), NextAction.PASS, source=source)
        labels = {item[0]: item[1] for item in self.diagnostic.hypotheses}
        cleaned = {key: max(0.0, probabilities.get(key, 0.0)) for key in labels}
        total = sum(cleaned.values())
        cleaned = ({key: value / total for key, value in cleaned.items()} if total else {key: 1 / len(labels) for key in labels})
        hypotheses = tuple(
            Hypothesis(key, labels[key], round(value, 4), (evidence or {}).get(key, "This interpretation remains plausible."))
            for key, value in sorted(cleaned.items(), key=lambda item: item[1], reverse=True)
        )
        return Analysis(correctness, reasoning_quality, hypotheses, NextAction.PROBE, self.diagnostic.probe, source)

    def apply_probe(self, analysis: Analysis, answer: str):
        if analysis.probe is None:
            raise ValueError("Analysis has no diagnostic probe")
        priors = {item.id: item.probability for item in analysis.hypotheses}
        posteriors = update_beliefs(priors, analysis.probe, answer)
        labels = {item[0]: item[1] for item in self.diagnostic.hypotheses}
        hypotheses = tuple(
            Hypothesis(key, labels[key], round(value, 4), "The probe response supports this diagnosis.")
            for key, value in sorted(posteriors.items(), key=lambda item: item[1], reverse=True)
        )
        winner = hypotheses[0]
        if winner.probability < .62:
            return hypotheses, None, None
        return hypotheses, winner.id, self.diagnostic.lessons[winner.id]


def engine_for(concept_id: str):
    diagnostic = DIAGNOSTICS.get(concept_id)
    return ConceptDiagnosticEngine(concept_id, diagnostic) if diagnostic else DiagnosticEngine()
