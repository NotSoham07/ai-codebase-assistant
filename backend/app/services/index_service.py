from __future__ import annotations
import os
import pathlib
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from app.settings import settings
from app.schemas import IndexRepoRequest
from app.services.repo_service import ensure_repo_cloned, repo_dir
from app.services.text_utils import should_include, chunk_text
from app.services.vector_store import FaissStore
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
def _iter_files(root: str):
    for p in pathlib.Path(root).rglob("*"):
        if p.is_file():
            yield p

def index_repo(req: IndexRepoRequest) -> dict:
    rid = ensure_repo_cloned(req.repo_url, req.branch)
    root = repo_dir(rid)

    client = OpenAI(api_key=settings.openai_api_key)

    index_base = os.path.join(settings.data_dir, "indexes", rid)
    index_path = os.path.join(index_base, "index.faiss")
    chunks_path = os.path.join(index_base, "chunks.json")

    # We'll discover embedding dimension on first call.
    dim = None
    store = None

    files_indexed = 0
    chunks_indexed = 0

    # batch embed for speed
    batch_texts = []
    batch_metas = []

    def flush_batch():
        nonlocal dim, store, chunks_indexed
        if not batch_texts:
            return

        vectors = embedding_model.encode(batch_texts)
        vectors = np.array(vectors).astype(np.float32)
        if dim is None:
            dim = vectors.shape[1]
            store = FaissStore(dim=dim, index_path=index_path, chunks_path=chunks_path)
            store.create_new()

        store.add(vectors, batch_metas)
        chunks_indexed += len(batch_texts)
        batch_texts.clear()
        batch_metas.clear()

    max_files = settings.index_max_files
    max_bytes = settings.index_max_file_bytes

    for p in _iter_files(root):
        rel = str(p.relative_to(root)).replace("\\", "/")

        if not should_include(rel, req.include_globs, req.exclude_globs):
            continue

        if files_indexed >= max_files:
            break

        try:
            if p.stat().st_size > max_bytes:
                continue

            text = p.read_text(encoding="utf-8", errors="ignore")
            if not text.strip():
                continue

            chunks = chunk_text(text, settings.chunk_size_chars, settings.chunk_overlap_chars)
            for idx, ch in enumerate(chunks):
                batch_texts.append(ch)
                batch_metas.append({
                    "path": rel,
                    "chunk_index": idx,
                    "text": ch,
                    "full_text": None,  # not stored to save space
                })

                # flush every N chunks
                if len(batch_texts) >= 64:
                    flush_batch()

            files_indexed += 1
        except Exception:
            continue

    flush_batch()

    if store is None:
        raise ValueError("No files were indexed. Try adjusting include/exclude globs.")

    store.save()

    return {
        "repo_id": rid,
        "files_indexed": files_indexed,
        "chunks_indexed": chunks_indexed,
    }