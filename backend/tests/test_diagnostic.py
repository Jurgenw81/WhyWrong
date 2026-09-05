import unittest

from backend.diagnostic.engine import (
    DiagnosticEngine,
    OPTIMIZER_CONFUSION,
)
from backend.diagnostic.models import NextAction


class DiagnosticEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = DiagnosticEngine()

    def test_detects_multiple_optimizer_confusion_phrasings(self) -> None:
        answers = (
            "Backprop changes the weights.",
            "It calculates gradients then adjusts parameters.",
            "Backprop finds the gradients and updates the weights.",
            "It updates weights based on the loss.",
            "It computes derivatives and applies them to the parameters.",
        )
        for answer in answers:
            with self.subTest(answer=answer):
                analysis = self.engine.analyze(answer)
                self.assertEqual(analysis.next_action, NextAction.PROBE)
                self.assertEqual(analysis.hypotheses[0].id, OPTIMIZER_CONFUSION)

    def test_recognizes_correct_distinction(self) -> None:
        answer = (
            "Backprop computes gradients of the loss with respect to the "
            "parameters. The optimizer subsequently uses those gradients to "
            "update the parameters."
        )
        analysis = self.engine.analyze(answer)
        self.assertEqual(analysis.next_action, NextAction.PASS)
        self.assertGreater(analysis.correctness, 0.9)

    def test_ambiguous_answer_triggers_probe(self) -> None:
        analysis = self.engine.analyze(
            "It uses the loss to figure out how the network should change."
        )
        self.assertEqual(analysis.next_action, NextAction.PROBE)
        self.assertIsNotNone(analysis.probe)

    def test_yes_to_no_optimizer_probe_confirms_confusion(self) -> None:
        analysis = self.engine.analyze("Backprop updates the weights.")
        hypotheses, misconception, lesson = self.engine.apply_probe(analysis, "yes")
        self.assertEqual(misconception, OPTIMIZER_CONFUSION)
        self.assertGreater(hypotheses[0].probability, 0.8)
        self.assertIn("optimizer", lesson.lower())

    def test_probe_answers_are_case_and_whitespace_insensitive(self) -> None:
        analysis = self.engine.analyze("Backprop updates the weights.")
        for answer in ("yes", "YES", "  Yes  "):
            with self.subTest(answer=answer):
                _, misconception, _ = self.engine.apply_probe(analysis, answer)
                self.assertEqual(misconception, OPTIMIZER_CONFUSION)

        canonical = self.engine.apply_probe(analysis, "No")
        normalized = self.engine.apply_probe(analysis, "  NO ")
        self.assertEqual(normalized, canonical)


if __name__ == "__main__":
    unittest.main()
