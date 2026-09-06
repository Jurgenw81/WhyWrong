import unittest
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from backend.api.main import app, session_store


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        session_store.clear()
        self.client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def start_session(self) -> str:
        response = await self.client.post(
            "/api/sessions", json={"concept_id": "backpropagation"}
        )
        self.assertEqual(response.status_code, 201)
        return response.json()["session_id"]

    async def test_health(self) -> None:
        response = await self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn(response.json()["classifier"], {"deterministic", "openai"})

    async def test_openai_mode_reads_client_ip_from_http_request(self) -> None:
        class FakeClassifier:
            model = "test-model"

            async def analyze(self, answer, engine):
                return engine.analyze(answer)

        session_id = await self.start_session()
        with patch("backend.api.main.llm_classifier", FakeClassifier()):
            response = await self.client.post(
                f"/api/sessions/{session_id}/answer",
                json={"answer": "it fixes the loss"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["next_action"], "probe")

    async def test_lists_neural_network_concepts(self) -> None:
        response = await self.client.get("/api/concepts")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 12)
        self.assertEqual(body[0]["id"], "neural_networks")
        self.assertEqual(body[-1]["id"], "overfitting")
        self.assertTrue(all(item["explanation"] for item in body))
        self.assertTrue(all(item["example"] for item in body))

    async def test_every_curriculum_topic_has_a_topic_specific_diagnostic(self) -> None:
        concepts = (await self.client.get("/api/concepts")).json()
        for concept in concepts:
            with self.subTest(concept=concept["id"]):
                response = await self.client.post(
                    "/api/sessions", json={"concept_id": concept["id"]}
                )
                session_id = response.json()["session_id"]
                response = await self.client.post(
                    f"/api/sessions/{session_id}/answer",
                    json={"answer": "I am not sure yet."},
                )
                body = response.json()
                self.assertEqual(body["next_action"], "probe")
                self.assertEqual(len(body["hypotheses"]), 2)
                if concept["id"] != "backpropagation":
                    self.assertNotEqual(body["hypotheses"][0]["id"], "optimizer_confusion")

    async def test_additional_concept_has_its_own_diagnostic_loop(self) -> None:
        response = await self.client.post(
            "/api/sessions", json={"concept_id": "learning_rate"}
        )
        self.assertEqual(response.status_code, 201)
        session_id = response.json()["session_id"]

        response = await self.client.post(
            f"/api/sessions/{session_id}/answer",
            json={"answer": "A higher learning rate always makes training faster."},
        )
        body = response.json()
        self.assertEqual(body["next_action"], "probe")
        self.assertEqual(body["hypotheses"][0]["id"], "higher_is_always_faster")

        response = await self.client.post(
            f"/api/sessions/{session_id}/probe", json={"answer": "No"}
        )
        body = response.json()
        self.assertEqual(body["next_action"], "intervene")
        self.assertEqual(body["misconception_id"], "higher_is_always_faster")
        self.assertIn("overshoot", body["lesson"].lower())

    async def test_complete_diagnostic_loop(self) -> None:
        session_id = await self.start_session()
        response = await self.client.post(
            f"/api/sessions/{session_id}/answer",
            json={"answer": "Backprop updates the weights."},
        )
        self.assertEqual(response.json()["next_action"], "probe")
        self.assertEqual(response.json()["analysis_source"], "deterministic")

        response = await self.client.post(
            f"/api/sessions/{session_id}/probe", json={"answer": "yes"}
        )
        body = response.json()
        self.assertEqual(body["next_action"], "intervene")
        self.assertEqual(body["misconception_id"], "optimizer_confusion")
        self.assertIn("optimizer", body["lesson"].lower())
        self.assertIn("optimizer_confusion", body["state"]["misconceptions"])

        response = await self.client.post(
            f"/api/sessions/{session_id}/answer",
            json={
                "answer": (
                    "Backprop computes gradients. The optimizer uses those "
                    "gradients to update the parameters."
                )
            },
        )
        body = response.json()
        self.assertEqual(body["next_action"], "pass")
        self.assertEqual(body["state"]["evidence_count"], 2)
        self.assertEqual(body["state"]["misconceptions"], [])
        self.assertEqual(
            (await self.client.get(f"/api/sessions/{session_id}")).json()["phase"],
            "complete",
        )

    async def test_rejects_probe_when_none_is_pending(self) -> None:
        session_id = await self.start_session()
        response = await self.client.post(
            f"/api/sessions/{session_id}/probe", json={"answer": "yes"}
        )
        self.assertEqual(response.status_code, 409)

    async def test_unknown_concept_is_not_found(self) -> None:
        response = await self.client.post(
            "/api/sessions", json={"concept_id": "telepathy"}
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
