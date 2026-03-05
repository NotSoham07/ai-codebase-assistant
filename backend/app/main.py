from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import IndexRepoRequest, IndexRepoResponse, QueryRequest, QueryResponse
from app.services.index_service import index_repo
from app.services.rag_service import answer_question
from app.services.repo_service import list_repos

app = FastAPI(title="AI Codebase Assistant", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/repos")
def repos():
    return {"repos": list_repos()}

@app.post("/index", response_model=IndexRepoResponse)
def index(req: IndexRepoRequest):
    try:
        result = index_repo(req)
        return IndexRepoResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        result = answer_question(req.repo_id, req.question, top_k=req.top_k)
        return QueryResponse(**result)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="repo_id not found. Index it first.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))