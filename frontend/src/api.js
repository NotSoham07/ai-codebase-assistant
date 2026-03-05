const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function indexRepo(payload) {
  const res = await fetch(`${API_BASE}/index`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Index failed");
  return res.json();
}

export async function queryRepo(payload) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Query failed");
  return res.json();
}