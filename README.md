# AI Codebase Assistant (RAG)

An AI-powered developer assistant that indexes a GitHub repo and answers questions using:
- OpenAI embeddings (vector search)
- FAISS for retrieval
- OpenAI Responses API for final answers

## Features
- Index any public GitHub repo URL
- Semantic search across code and docs
- Answer questions with file citations
- React chat UI + FastAPI backend
- Docker + docker-compose

## Quickstart (Docker)
1) Create `.env` from `.env.example` and add `OPENAI_API_KEY`
2) Run:
```bash
docker compose up --build