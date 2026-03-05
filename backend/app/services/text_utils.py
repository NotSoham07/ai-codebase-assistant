from __future__ import annotations
import fnmatch

DEFAULT_EXCLUDES = [
    "**/.git/**",
    "**/node_modules/**",
    "**/dist/**",
    "**/build/**",
    "**/.venv/**",
    "**/venv/**",
    "**/__pycache__/**",
    "**/*.png",
    "**/*.jpg",
    "**/*.jpeg",
    "**/*.gif",
    "**/*.pdf",
    "**/*.zip",
    "**/*.tar",
    "**/*.gz",
    "**/*.lock",
]

def should_include(path: str, include_globs: list[str] | None, exclude_globs: list[str] | None) -> bool:
    ex = (exclude_globs or []) + DEFAULT_EXCLUDES
    for pat in ex:
        if fnmatch.fnmatch(path, pat):
            return False

    if not include_globs:
        return True

    return any(fnmatch.fnmatch(path, pat) for pat in include_globs)

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= 0:
        return [text]
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + chunk_size)
        chunks.append(text[i:j])
        if j == n:
            break
        i = max(0, j - overlap)
    return chunks

def line_range_for_snippet(full_text: str, snippet: str) -> tuple[int, int]:
    idx = full_text.find(snippet)
    if idx < 0:
        return (1, 1)
    start_line = full_text.count("\n", 0, idx) + 1
    end_line = start_line + snippet.count("\n")
    return (start_line, end_line)