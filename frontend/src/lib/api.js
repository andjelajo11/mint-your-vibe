const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function generateCard(prompt) {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || "Something went wrong generating that.");
  }

  return res.json();
}

export async function fetchGallery(limit = 20) {
  const res = await fetch(`${API_BASE}/gallery?limit=${limit}`);
  if (!res.ok) throw new Error("Couldn't load the gallery.");
  return res.json();
}
