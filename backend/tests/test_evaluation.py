import tempfile
import unittest
from pathlib import Path

from backend.diagnostic.engine import DiagnosticEngine
from backend.evaluation.dataset import load_dataset
from backend.evaluation.metrics import EvaluationResult, summarize
from backend.evaluation.report import render_markdown, write_reports
from backend.evaluation.runner import evaluate, prediction_for


class EvaluationDatasetTests(unittest.TestCase):
    def test_dataset_is_balanced_and_has_unique_ids(self) -> None:
        examples = load_dataset()

        self.assertEqual(len(examples), 48)
        self.assertEqual(len({item.id for item in examples}), 48)
        for label in (
            "correct",
            "optimizer_confusion",
            "gradient_misunderstanding",
            "ambiguous",
        ):
            self.assertEqual(sum(item.label == label for item in examples), 12)


class EvaluationRunnerTests(unittest.IsolatedAsyncioTestCase):
    def test_prediction_maps_a_correct_answer_to_correct(self) -> None:
        analysis = DiagnosticEngine().analyze(
            "Backprop computes gradients and the optimizer uses them to update weights."
        )

        self.assertEqual(prediction_for(analysis), "correct")

    async def test_deterministic_evaluation_returns_every_result(self) -> None:
        examples = load_dataset()[:4]

        summary = await evaluate(examples, provider="deterministic")

        self.assertEqual(summary.total, 4)
        self.assertEqual(len(summary.results), 4)
        self.assertTrue(all(item.source == "deterministic" for item in summary.results))


class EvaluationReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = summarize(
            [
                EvaluationResult("a", "correct", "correct", True, "deterministic"),
                EvaluationResult(
                    "b",
                    "optimizer_confusion",
                    "ambiguous",
                    False,
                    "deterministic",
                ),
            ]
        )

    def test_summary_and_markdown_show_actual_score(self) -> None:
        self.assertEqual(self.summary.accuracy, 0.5)
        report = render_markdown(self.summary, "deterministic")
        self.assertIn("50.0%", report)
        self.assertIn("`b`", report)

    def test_write_reports_creates_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation.md"
            markdown_path, json_path = write_reports(
                self.summary, "deterministic", output
            )

            self.assertTrue(markdown_path.is_file())
            self.assertTrue(json_path.is_file())
            self.assertIn('"total": 2', json_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
