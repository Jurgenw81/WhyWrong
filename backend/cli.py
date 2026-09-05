from __future__ import annotations

from backend.diagnostic import DiagnosticEngine, MasteryEngine
from backend.diagnostic.models import ConceptState, NextAction


QUESTION = (
    "During training, what role does backpropagation play in changing the "
    "weights of a neural network?"
)


def main() -> None:
    engine = DiagnosticEngine()
    mastery = MasteryEngine()
    state = ConceptState("backpropagation")

    print("WhyWrong — Don't just correct mistakes. Understand them.\n")
    print(QUESTION)
    answer = input("> ")
    analysis = engine.analyze(answer)

    if analysis.next_action is NextAction.PASS:
        mastery.update(state, correct=True)
        print(f"\nThat distinction is correct. Mastery: {state.mastery_probability:.0%}")
        return

    print("\nI see two possible interpretations. Let's check which one you mean.")
    assert analysis.probe is not None
    print(analysis.probe.question)
    print(" / ".join(analysis.probe.choices))
    probe_answer = input("> ").strip()
    hypotheses, misconception, lesson = engine.apply_probe(analysis, probe_answer)

    print("\nUpdated hypotheses:")
    for hypothesis in hypotheses:
        print(f"- {hypothesis.label}: {hypothesis.probability:.0%}")

    if misconception is None:
        print("I need one more piece of evidence before diagnosing this confidently.")
        return

    mastery.update(state, correct=False, misconception_id=misconception)
    print(f"\nRoot misconception: {hypotheses[0].label}\n{lesson}")
    print("\nTry the original question again:")
    print(QUESTION)
    retry = input("> ")
    retry_analysis = engine.analyze(retry)
    retry_correct = retry_analysis.next_action is NextAction.PASS
    mastery.update(state, correct=retry_correct, misconception_id=misconception)
    print(
        f"\n{'Correct' if retry_correct else 'Still diagnosing'}. "
        f"Mastery: {state.mastery_probability:.0%}"
    )


if __name__ == "__main__":
    main()

