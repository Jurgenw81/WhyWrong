from __future__ import annotations

import re

from .models import Analysis, Hypothesis, NextAction, Probe
from .probes import select_probe, update_beliefs


OPTIMIZER_CONFUSION = "optimizer_confusion"
GRADIENT_MISUNDERSTANDING = "gradient_misunderstanding"


PROBES = (
    Probe(
        id="weights_without_optimizer",
        question=(
            "Suppose we run the forward pass and backpropagation, but never "
            "call the optimizer. Will the model's weights change?"
        ),
        choices=("Yes", "No", "Not sure"),
        likelihoods={
            OPTIMIZER_CONFUSION: {"Yes": 0.86, "No": 0.05, "Not sure": 0.09},
            GRADIENT_MISUNDERSTANDING: {"Yes": 0.25, "No": 0.50, "Not sure": 0.25},
        },
    ),
    Probe(
        id="meaning_of_gradient",
        question="Is a gradient a parameter change, or information used to choose one?",
        choices=("Parameter change", "Information", "Not sure"),
        likelihoods={
            OPTIMIZER_CONFUSION: {
                "Parameter change": 0.48,
                "Information": 0.42,
                "Not sure": 0.10,
            },
            GRADIENT_MISUNDERSTANDING: {
                "Parameter change": 0.78,
                "Information": 0.08,
                "Not sure": 0.14,
            },
        },
    ),
)


MICRO_LESSONS = {
    OPTIMIZER_CONFUSION: (
        "Backpropagation computes gradients: signals describing how the loss "
        "changes with each parameter. The optimizer is a separate step that "
        "uses those gradients (plus its update rule) to change the weights."
    ),
    GRADIENT_MISUNDERSTANDING: (
        "A gradient is not itself a weight change. It describes the local slope "
        "of the loss. An optimizer turns that information into a parameter update."
    ),
}


class DiagnosticEngine:
    """Application-controlled diagnostic loop with replaceable classification."""

    _correct_patterns = (
        r"comput\w* gradients?.*optimizer.*(?:update|change|adjust)",
        r"optimizer.*(?:use|apply).*gradients?.*(?:update|change|adjust)",
        r"gradients?.*(?:with respect to|wrt).*parameters?.*optimizer",
    )
    _update_patterns = (
        r"backprop\w*.*(?:update|change|adjust|apply).*(?:weight|parameter)",
        r"(?:update|change|adjust).*(?:weight|parameter).*backprop",
        r"comput\w*.*gradient.*(?:and|then).*(?:update|change|adjust|apply)",
    )
    _gradient_patterns = (
        r"gradient.*(?:is|are|means?).*(?:weight|parameter).*(?:change|update)",
        r"how much.*(?:weight|parameter).*(?:will|should).*(?:change|update)",
    )

    def analyze(self, answer: str) -> Analysis:
        text = " ".join(answer.lower().split())
        if any(re.search(pattern, text) for pattern in self._correct_patterns):
            return Analysis(0.96, 0.9, (), NextAction.PASS)

        optimizer_score = 0.78 if any(
            re.search(pattern, text) for pattern in self._update_patterns
        ) else 0.44
        gradient_score = 0.72 if any(
            re.search(pattern, text) for pattern in self._gradient_patterns
        ) else 0.22

        if not text or len(text.split()) < 4:
            optimizer_score, gradient_score = 0.5, 0.5

        total = optimizer_score + gradient_score
        probabilities = {
            OPTIMIZER_CONFUSION: optimizer_score / total,
            GRADIENT_MISUNDERSTANDING: gradient_score / total,
        }
        hypotheses = self._make_hypotheses(probabilities)
        probe = select_probe(probabilities, PROBES)
        return Analysis(0.3, 0.55, hypotheses, NextAction.PROBE, probe)

    def apply_probe(
        self, analysis: Analysis, answer: str
    ) -> tuple[tuple[Hypothesis, ...], str | None, str | None]:
        if analysis.probe is None:
            raise ValueError("Analysis has no diagnostic probe")
        priors = {item.id: item.probability for item in analysis.hypotheses}
        posteriors = update_beliefs(priors, analysis.probe, answer)
        hypotheses = self._make_hypotheses(posteriors)
        winner = max(posteriors, key=posteriors.get)
        if posteriors[winner] < 0.72:
            return hypotheses, None, None
        return hypotheses, winner, MICRO_LESSONS[winner]

    @staticmethod
    def _make_hypotheses(probabilities: dict[str, float]) -> tuple[Hypothesis, ...]:
        labels = {
            OPTIMIZER_CONFUSION: "Backpropagation / optimizer confusion",
            GRADIENT_MISUNDERSTANDING: "Gradient misunderstanding",
        }
        evidence = {
            OPTIMIZER_CONFUSION: (
                "The response may attribute parameter updates to backpropagation."
            ),
            GRADIENT_MISUNDERSTANDING: (
                "The response may treat a gradient as the update itself."
            ),
        }
        return tuple(
            Hypothesis(key, labels[key], round(value, 4), evidence[key])
            for key, value in sorted(
                probabilities.items(), key=lambda item: item[1], reverse=True
            )
        )

