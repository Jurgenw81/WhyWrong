async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : null;
  if (!response.ok) {
    throw new Error(
      payload?.detail ||
        `The server returned an error (${response.status}). Please try again.`,
    );
  }
  if (payload === null) {
    throw new Error("The server returned an invalid response. Please try again.");
  }
  return payload;
}

export function getConcepts() {
  return request("/api/concepts");
}

export function startSession(conceptId = "backpropagation") {
  return request("/api/sessions", {
    method: "POST",
    body: JSON.stringify({ concept_id: conceptId }),
  });
}

export function submitAnswer(sessionId, answer) {
  return request(`/api/sessions/${sessionId}/answer`, {
    method: "POST",
    body: JSON.stringify({ answer }),
  });
}

export function submitProbe(sessionId, answer) {
  return request(`/api/sessions/${sessionId}/probe`, {
    method: "POST",
    body: JSON.stringify({ answer }),
  });
}
