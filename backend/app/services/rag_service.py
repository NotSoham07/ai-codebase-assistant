from __future__ import annotations

import os
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from app.settings import settings
from app.services.vector_store import FaissStore
from app.services.repo_service import repo_dir
from app.services.text_utils import line_range_for_snippet


# Load embedding model once (fast + local)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def _load_store(repo_id: str) -> FaissStore:

    base = os.path.join(settings.data_dir, "indexes", repo_id)

    index_path = os.path.join(base, "index.faiss")
    chunks_path = os.path.join(base, "chunks.json")

    if not (os.path.exists(index_path) and os.path.exists(chunks_path)):
        raise FileNotFoundError(repo_id)

    store = FaissStore(dim=1, index_path=index_path, chunks_path=chunks_path)
    store.load()
    store.dim = store.index.d

    return store


def answer_question(repo_id: str, question: str, top_k: int = 8) -> dict:

    # Connect to Scitely API
    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url
    )

    store = _load_store(repo_id)

    # Create embedding for the user question
    q_vec = embedding_model.encode([question])
    q_vec = np.array(q_vec).astype(np.float32)

    hits = store.search(q_vec, top_k=top_k)

    retrieved = []
    citations = []

    root = repo_dir(repo_id)

    context_blocks = []

    for score, meta in hits:

        path = meta["path"]
        snippet = meta["text"]

        retrieved.append({
            "path": path,
            "score": score,
            "snippet": snippet[:500] + ("..." if len(snippet) > 500 else "")
        })

        full_path = os.path.join(root, path)

        try:
            full_text = open(full_path, "r", encoding="utf-8", errors="ignore").read()
            start_line, end_line = line_range_for_snippet(full_text, snippet)
        except Exception:
            start_line, end_line = 1, 1

        citations.append({
            "path": path,
            "start_line": start_line,
            "end_line": end_line
        })

        context_blocks.append(
            f"FILE: {path}\n---\n{snippet}\n"
        )

    system = (
        "You are an expert software engineer. "
        "Answer questions about a codebase using the provided code snippets. "
        "If the answer is not in the context, explain what files should be inspected."
    )

    context_text = "\n".join(context_blocks)

    prompt = f"""{system}

CONTEXT:
{context_text}

QUESTION:
{question}

RESPONSE RULES:
- Be concise but clear
- Mention filenames when relevant
- Include short code snippets if helpful
"""

    # Send to Scitely LLM
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "citations": citations,
        "retrieved": retrieved,
    }