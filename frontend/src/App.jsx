import React, { useState } from "react";
import { indexRepo, queryRepo } from "./api";
import "./styles.css";

export default function App() {

  const [repoUrl, setRepoUrl] = useState("https://github.com/pallets/flask");
  const [repoId, setRepoId] = useState("");
  const [status, setStatus] = useState("");

  const [question, setQuestion] = useState("Where is authentication implemented?");
  const [prUrl, setPrUrl] = useState("");

  const [messages, setMessages] = useState([]);

  async function handleIndex() {
    setStatus("Indexing… (first time can take a bit depending on repo size)");

    try {
      const out = await indexRepo({ repo_url: repoUrl });

      setRepoId(out.repo_id);

      setStatus(
        `Indexed repo_id=${out.repo_id} | files=${out.files_indexed} | chunks=${out.chunks_indexed}`
      );

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

      const out = await queryRepo({
        repo_id: repoId,
        question: q,
        top_k: 8
      });

      setMessages((m) => [
        ...m,
        { role: "ai", text: out.answer, citations: out.citations }
      ]);

      setStatus("Done.");

    } catch (e) {
      setStatus(`Query failed: ${e.message}`);
    }
  }

  async function handlePRReview() {

    if (!prUrl) return;

    setMessages((m) => [...m, { role: "user", text: `Review PR: ${prUrl}` }]);

    setStatus("Analyzing PR…");

    try {

      const res = await fetch("http://localhost:8000/review-pr", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ pr_url: prUrl })
      });

      const data = await res.json();

      setMessages((m) => [
        ...m,
        { role: "ai", text: data.review }
      ]);

      setStatus("PR review complete.");

      setPrUrl("");

    } catch (e) {

      setStatus(`PR review failed: ${e.message}`);

    }
  }

  return (
    <div className="container">

      <h2>AI Codebase Assistant</h2>

      <div className="card">

        {/* Repo indexing */}
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

        {/* Ask questions */}
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

        <hr />

        {/* PR Review */}
        <div className="row">

          <input
            style={{ flex: 1, minWidth: 320 }}
            value={prUrl}
            onChange={(e) => setPrUrl(e.target.value)}
            placeholder="Paste GitHub PR URL to review"
          />

          <button onClick={handlePRReview}>
            Review PR
          </button>

        </div>

        <div className="small" style={{ marginTop: 10 }}>
          {status}
        </div>

        {/* Chat history */}

        <div style={{ marginTop: 14 }}>

          {messages.map((m, idx) => (

            <div key={idx} className={`msg ${m.role === "user" ? "user" : "ai"}`}>

              <pre>
                <b>{m.role === "user" ? "You" : "Assistant"}:</b> {m.text}
              </pre>

              {m.citations?.length ? (

                <div className="small" style={{ marginTop: 10 }}>

                  <b>Citations:</b>

                  <ul>

                    {m.citations.slice(0, 6).map((c, i) => (
                      <li key={i}>
                        {c.path}:{c.start_line}-{c.end_line}
                      </li>
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