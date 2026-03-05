# AI Codebase Assistant

An AI-powered developer assistant that indexes GitHub repositories and answers questions about the codebase using Retrieval-Augmented Generation (RAG).

## Features

• Index any public GitHub repository  
• Semantic code search using vector embeddings  
• AI explanations of code architecture  
• File-level citations for responses  
• React-based chat interface  

## Architecture

Frontend  
React + Vite

Backend  
FastAPI

AI Stack  
SentenceTransformers embeddings  
FAISS vector search  
Qwen3-Coder-Plus via Scitely API

Infrastructure  
Docker containers

## System Flow

1. Clone GitHub repository
2. Split files into chunks
3. Generate embeddings
4. Store vectors in FAISS
5. Retrieve relevant code snippets
6. Send context to LLM
7. Generate explanation

## Demo

1. Index a repository:

https://github.com/tiangolo/fastapi

2. Ask:

Explain how routing works

The assistant retrieves relevant code and generates an explanation with file references.

## Tech Stack

Python  
FastAPI  
React  
Docker  
FAISS  
SentenceTransformers  
Scitely API (Qwen3) - Free API prompts

## Future Improvements

• GitHub PR review assistant  
• Architecture diagram generation  
• Repo dependency graph visualization  
