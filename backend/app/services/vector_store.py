from __future__ import annotations
import os
import json
import numpy as np
import faiss

class FaissStore:
    """
    Minimal FAISS wrapper with:
      - index.faiss
      - chunks.json (metadata + text)
    """
    def __init__(self, dim: int, index_path: str, chunks_path: str):
        self.dim = dim
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.index = None
        self.chunks = []

    def create_new(self):
        self.index = faiss.IndexFlatIP(self.dim)

    def add(self, vectors: np.ndarray, metadatas: list[dict]):
        if self.index is None:
            raise RuntimeError("Index not initialized")
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)

        # normalize for cosine similarity via inner product
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.chunks.extend(metadatas)

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False)

    def load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

    def search(self, query_vec: np.ndarray, top_k: int = 8):
        if query_vec.dtype != np.float32:
            query_vec = query_vec.astype(np.float32)
        faiss.normalize_L2(query_vec)

        scores, idxs = self.index.search(query_vec, top_k)
        results = []
        for score, i in zip(scores[0], idxs[0]):
            if i < 0:
                continue
            meta = self.chunks[i]
            results.append((float(score), meta))
        return results