# LedgerLens: AI Investigation System

A production-ready Structured RAG investigation system built with FastAPI, LangGraph, GROQ, PostgreSQL + pgvector, and Redis.

## Features Enforced

- **Tool-First Architecture**: Deterministic factual extractions (`get_transaction`, `reconcile_account`, etc.)
- **Zero Hallucination Policy**: If evidence doesn't answer the intent, the system aborts (`INSUFFICIENT_EVIDENCE`).
- **Production Safety**: Confidence scoring checks, JWT RBAC Auth, structured JSON responses.
- **RAG + Vector**: Uses `pgvector` with HNSW indexes and SentenceTransformers for semantic retrieval of old tickets.

## How to Run locally

### 1. Configure the Environment
Create a `.env` file from the example or simply export your API key:
```bash
export GROQ_API_KEY="gsk_..."
```

### 2. Start the Docker Infrastructure
We provide a `docker-compose.yml` that mounts the API, PostgreSQL(pgvector), and Redis.

```bash
cd docker
docker-compose up --build -d
```

### 3. Initialize the Database & Seed Data
Once the containers are healthy, you must create the schema and seed mock transactions.
```bash
docker exec -it docker-api-1 python scripts/seed_db.py
```

### 4. Query the API
Use the provided `create_mock_token` in `app/core/security.py` or hit it directly bypassing token if dev mode is modified, otherwise:

```bash
# Example Request Format (Requires JWT Auth headers in production)
curl -X POST http://localhost:8000/investigate \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     -d '{"query": "Why did transaction TXN-102 fail?"}'
```

## Validation Checklist
- [x] Phase 1: Architecture Design 
- [x] Phase 2: Project Structure (Fully built python module structure)
- [x] Phase 3: Database Design (SQLAlchemy + pgvector models & seeds)
- [x] Phase 4: Tooling Layer (Fast exact match scripts)
- [x] Phase 5: RAG Retrieval System (Redis + RRF Hybrid search)
- [x] Phase 6: Agent Orchestration (LangGraph Flow)
- [x] Phase 7: Groq LLM Integration (Llama-3.3-70b-versatile via Langchain)
- [x] Phase 8: Confidence & Guardrails (0.0-1.0 scoring, Abstention Logic)
- [x] Phase 9: FastAPI Service (Exposes /investigate)
- [x] Phase 10: Evaluation Pipeline (Eval tools & Golden DB)
- [x] Phase 11: Caching & Performance (Redis cache for RAG)
- [x] Phase 12: Docker Deployment (Dockerfile + PGVector + Redis Compose)
- [x] Phase 13: Observability (Decorators and Loggers)
- [x] Phase 14: Testing (Metrics verification unit tests)
