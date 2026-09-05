async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Something went wrong");
  }
  return payload;
}

export function startSession() {
  return request("/api/sessions", {
    method: "POST",
    body: JSON.stringify({ concept_id: "backpropagation" }),
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
