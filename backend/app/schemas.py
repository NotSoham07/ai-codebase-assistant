from pydantic import BaseModel, Field
from typing import Optional, List

class IndexRepoRequest(BaseModel):
    repo_url: str = Field(..., examples=["https://github.com/pallets/flask"])
    branch: Optional[str] = None
    include_globs: Optional[List[str]] = None   # e.g. ["**/*.py", "**/*.md"]
    exclude_globs: Optional[List[str]] = None   # e.g. ["**/node_modules/**", "**/dist/**"]

class IndexRepoResponse(BaseModel):
    repo_id: str
    files_indexed: int
    chunks_indexed: int

class QueryRequest(BaseModel):
    repo_id: str
    question: str
    top_k: int = 8

class QueryResponse(BaseModel):
    answer: str
    citations: list[dict]  # {path, start_line, end_line}
    retrieved: list[dict]  # {path, score, snippet}