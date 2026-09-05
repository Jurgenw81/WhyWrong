import unittest

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
        self.assertEqual(response.json(), {"status": "ok"})

    async def test_complete_diagnostic_loop(self) -> None:
        session_id = await self.start_session()
        response = await self.client.post(
            f"/api/sessions/{session_id}/answer",
            json={"answer": "Backprop updates the weights."},
        )
        self.assertEqual(response.json()["next_action"], "probe")

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
