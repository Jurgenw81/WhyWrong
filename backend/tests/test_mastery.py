import unittest

from backend.diagnostic.mastery import MasteryEngine
from backend.diagnostic.models import ConceptState


class MasteryEngineTests(unittest.TestCase):
    def test_wrong_then_correct_tracks_misconception_and_recovery(self) -> None:
        engine = MasteryEngine()
        state = ConceptState("backpropagation")
        engine.update(state, correct=False, misconception_id="optimizer_confusion")
        after_error = state.mastery_probability
        self.assertIn("optimizer_confusion", state.misconceptions)

        engine.update(state, correct=True, misconception_id="optimizer_confusion")
        self.assertGreater(state.mastery_probability, after_error)
        self.assertNotIn("optimizer_confusion", state.misconceptions)
        self.assertEqual(state.evidence_count, 2)


if __name__ == "__main__":
    unittest.main()

