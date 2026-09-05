from __future__ import annotations

from math import log2

from .models import Probe


def entropy(probabilities: list[float]) -> float:
    return -sum(p * log2(p) for p in probabilities if p > 0)


def expected_information_gain(
    priors: dict[str, float], probe: Probe
) -> float:
    """Return H(hypotheses) - E[H(hypotheses | answer)]."""
    prior_entropy = entropy(list(priors.values()))
    expected_posterior_entropy = 0.0

    for answer in probe.choices:
        answer_probability = sum(
            priors[hypothesis] * probe.likelihoods[hypothesis].get(answer, 0.0)
            for hypothesis in priors
        )
        if answer_probability == 0:
            continue
        posterior = [
            priors[hypothesis]
            * probe.likelihoods[hypothesis].get(answer, 0.0)
            / answer_probability
            for hypothesis in priors
        ]
        expected_posterior_entropy += answer_probability * entropy(posterior)

    return prior_entropy - expected_posterior_entropy


def select_probe(priors: dict[str, float], probes: tuple[Probe, ...]) -> Probe:
    compatible = tuple(
        probe for probe in probes if set(priors).issubset(probe.likelihoods)
    )
    if not compatible:
        raise ValueError("No probe covers all active hypotheses")
    return max(compatible, key=lambda probe: expected_information_gain(priors, probe))


def update_beliefs(
    priors: dict[str, float], probe: Probe, answer: str
) -> dict[str, float]:
    if answer not in probe.choices:
        raise ValueError(f"Unknown answer {answer!r}; expected one of {probe.choices}")

    unnormalized = {
        hypothesis: probability * probe.likelihoods[hypothesis].get(answer, 0.0)
        for hypothesis, probability in priors.items()
    }
    total = sum(unnormalized.values())
    if total == 0:
        return priors.copy()
    return {
        hypothesis: probability / total
        for hypothesis, probability in unnormalized.items()
    }

