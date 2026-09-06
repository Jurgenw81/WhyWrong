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
