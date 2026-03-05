import React, { useState } from "react";
import { indexRepo, queryRepo } from "./api";
import "./styles.css";

export default function App() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/pallets/flask");
  const [repoId, setRepoId] = useState("");
  const [status, setStatus] = useState("");
  const [question, setQuestion] = useState("Where is authentication implemented?");
  const [messages, setMessages] = useState([]);

  async function handleIndex() {
    setStatus("Indexing… (first time can take a bit depending on repo size)");
    try {
      const out = await indexRepo({ repo_url: repoUrl });
      setRepoId(out.repo_id);
      setStatus(`Indexed repo_id=${out.repo_id} | files=${out.files_indexed} | chunks=${out.chunks_indexed}`);
    } catch (e) {
      setStatus(`Index failed: ${e.message}`);
    }
  }

  async function handleAsk() {
    if (!repoId) {
      setStatus("Please index a repo first.");
      return;
    }
    const q = question.trim();
    if (!q) return;

    setMessages((m) => [...m, { role: "user", text: q }]);
    setQuestion("");
    setStatus("Thinking…");

    try {
      const out = await queryRepo({ repo_id: repoId, question: q, top_k: 8 });
      setMessages((m) => [...m, { role: "ai", text: out.answer, citations: out.citations }]);
      setStatus("Done.");
    } catch (e) {
      setStatus(`Query failed: ${e.message}`);
    }
  }

  return (
    <div className="container">
      <h2>AI Codebase Assistant</h2>
      <div className="card">
        <div className="row">
          <input
            style={{ flex: 1, minWidth: 320 }}
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="GitHub repo URL"
          />
          <button onClick={handleIndex}>Index Repo</button>
        </div>
        <div className="small" style={{ marginTop: 10 }}>
          repo_id: <b>{repoId || "—"}</b>
        </div>

        <hr />

        <div className="row">
          <input
            style={{ flex: 1, minWidth: 320 }}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about the repo…"
            onKeyDown={(e) => (e.key === "Enter" ? handleAsk() : null)}
          />
          <button onClick={handleAsk}>Ask</button>
        </div>

        <div className="small" style={{ marginTop: 10 }}>{status}</div>

        <div style={{ marginTop: 14 }}>
          {messages.map((m, idx) => (
            <div key={idx} className={`msg ${m.role === "user" ? "user" : "ai"}`}>
              <pre><b>{m.role === "user" ? "You" : "Assistant"}:</b> {m.text}</pre>
              {m.citations?.length ? (
                <div className="small" style={{ marginTop: 10 }}>
                  <b>Citations:</b>
                  <ul>
                    {m.citations.slice(0, 6).map((c, i) => (
                      <li key={i}>{c.path}:{c.start_line}-{c.end_line}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}