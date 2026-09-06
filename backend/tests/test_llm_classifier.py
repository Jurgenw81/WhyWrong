import unittest
from types import SimpleNamespace

from backend.diagnostic.engine import DiagnosticEngine, OPTIMIZER_CONFUSION
from backend.diagnostic.concept_engine import engine_for
from backend.diagnostic.llm_classifier import (
    MisconceptionAssessment,
    OpenAIAnswerClassifier,
    StructuredAssessment,
)
from backend.diagnostic.models import NextAction


class FakeResponses:
    def __init__(self, assessment: StructuredAssessment) -> None:
        self.assessment = assessment
        self.arguments = None

    async def parse(self, **kwargs):
        self.arguments = kwargs
        return SimpleNamespace(output_parsed=self.assessment)


class LlmClassifierTests(unittest.IsolatedAsyncioTestCase):
    async def test_maps_structured_output_into_diagnostic_loop(self) -> None:
        assessment = StructuredAssessment(
            correctness=0.28,
            reasoning_quality=0.7,
            misconceptions=[
                MisconceptionAssessment(
                    id="optimizer_confusion",
                    probability=0.88,
                    evidence="The student says backprop changes the weights.",
                ),
                MisconceptionAssessment(
                    id="gradient_misunderstanding",
                    probability=0.12,
                    evidence="The meaning of gradient remains unclear.",
                ),
            ],
        )
        responses = FakeResponses(assessment)
        client = SimpleNamespace(responses=responses)
        classifier = OpenAIAnswerClassifier(client=client, model="test-model")

        analysis = await classifier.analyze(
            "Backprop fixes the weights.", DiagnosticEngine()
        )

        self.assertEqual(analysis.next_action, NextAction.PROBE)
        self.assertEqual(analysis.hypotheses[0].id, OPTIMIZER_CONFUSION)
        self.assertEqual(analysis.source, "openai:test-model")
        self.assertEqual(responses.arguments["text_format"], StructuredAssessment)
        self.assertFalse(responses.arguments["store"])

    async def test_correct_structured_answer_passes(self) -> None:
        assessment = StructuredAssessment(
            correctness=0.95,
            reasoning_quality=0.9,
            misconceptions=[
                MisconceptionAssessment(
                    id="optimizer_confusion", probability=0.02, evidence="Distinguished."
                ),
                MisconceptionAssessment(
                    id="gradient_misunderstanding", probability=0.01, evidence="Defined."
                ),
            ],
        )
        client = SimpleNamespace(responses=FakeResponses(assessment))
        classifier = OpenAIAnswerClassifier(client=client, model="test-model")
        analysis = await classifier.analyze("Correct explanation", DiagnosticEngine())
        self.assertEqual(analysis.next_action, NextAction.PASS)

    async def test_uses_topic_specific_misconceptions(self) -> None:
        assessment = StructuredAssessment(
            correctness=0.2,
            reasoning_quality=0.4,
            misconceptions=[
                MisconceptionAssessment(
                    id="loss_updates_weights", probability=0.9, evidence="Says loss updates."
                ),
                MisconceptionAssessment(
                    id="loss_equals_accuracy", probability=0.1, evidence="No accuracy claim."
                ),
            ],
        )
        responses = FakeResponses(assessment)
        classifier = OpenAIAnswerClassifier(
            client=SimpleNamespace(responses=responses), model="test-model"
        )

        analysis = await classifier.analyze(
            "The loss changes the weights.", engine_for("loss_functions")
        )

        self.assertEqual(analysis.hypotheses[0].id, "loss_updates_weights")
        self.assertIn("loss_updates_weights", responses.arguments["instructions"])


if __name__ == "__main__":
    unittest.main()
