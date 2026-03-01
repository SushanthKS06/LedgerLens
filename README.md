# 🔍 LedgerLens: AI-Powered Financial Investigation System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?logo=postgresql)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-Supported-blue)](https://github.com/pgvector/pgvector)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-orange)](https://python.langchain.com/docs/langgraph)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-black)](https://groq.com/)

**LedgerLens** is a production-grade, end-to-end Structured RAG (Retrieval-Augmented Generation) system built for autonomous financial and operational investigations. It leverages deterministic tooling, advanced agent orchestration via LangGraph, and high-performance LLM inference via Groq to resolve complex financial discrepancies (e.g., payout mismatches, journal lineage issues, and reconciliation debugging) with **Zero Hallucination** guarantees.

---

## ✨ Core Features

- **🛡️ Zero Hallucination Policy:** The LLM acts purely as an orchestrator and synthesizer. All financial data is pulled strictly from deterministic tools and SQL queries. If evidence is insufficient, the system safely aborts.
- **🧠 Multi-Step Agentic RAG:** Powered by LangGraph, the agent flow dynamically resolves intent, selects tools, gathers evidence, synthesizes findings, and applies confidence guardrails.
- **⚡ High-Performance Architecture:** utilizing FastAPI for async endpoints, Groq (`llama-3.3-70b-versatile`) for blazing-fast inference, and Redis for aggressive caching of vector embeddings and exact-match queries.
- **📊 Hybrid Vector Search:** Integrates `pgvector` alongside PostgreSQL Full-Text Search (merged via Reciprocal Rank Fusion) to semantically find historically similar resolved tickets.
- **👮 Role-Based Access Control (RBAC):** Strict JWT-based authorization ensures users only execute tools they have explicit permission for.
- **🔬 Built-In Evaluation Pipeline:** Native support for evaluating agent accuracy with metrics like `Recall@K`, `Grounding Score`, and `Tool Accuracy` against golden datasets.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([User Request /investigate]) --> API[FastAPI Gateway]
    API --> Auth[RBAC Middleware]
    Auth --> Cache[Redis Cache]
    Cache --> Orchestrator[LangGraph Orchestrator]
    
    subgraph Agent Loop
        Orchestrator --> Intent[Intent & Tool Selector]
        Intent --> Tools[Deterministic SQL Tools]
        Intent --> RAG[Hybrid RAG System]
        
        RAG --> RedisKV[(Redis Embeddings Cache)]
        RAG --> VectorDB[(PostgreSQL + pgvector)]
        Tools --> CoreDB[(PostgreSQL Core DB)]
        
        Orchestrator --> LLM[Groq LLM: llama-3.3-70b]
        Orchestrator --> Guardrails[Confidence Scorer]
    end
```

---

## 🚀 Quick Start (Docker)

The easiest way to run LedgerLens is using the provided Docker Compose setup, which automatically provisions the API, PostgreSQL (with `pgvector`), and Redis.

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- A [Groq API Key](https://console.groq.com/keys)

### 2. Configuration
Create a `.env` file in the root directory (you can copy from `.env.example` if available):
```env
GROQ_API_KEY=gsk_your_actual_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ledgerlens
REDIS_URL=redis://redis:6379/0
```

### 3. Build & Run
```bash
# Start the infrastructure in detached mode
cd docker
docker-compose up --build -d
```

### 4. Initialize & Seed the Database
Once the containers are healthy, initialize the schema and seed mock financial data:
```bash
docker exec -it ledgerlens-api-1 python scripts/seed_db.py
```
*(Note: Your container name might differ slightly depending on your folder name, e.g., `docker-api-1`)*

---

## 💻 Local Development Setup

If you prefer running the Python server locally outside of Docker:

1. **Start backing services** (Postgres + Redis):
   ```bash
   docker-compose up db redis -d
   ```
2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Environment variables**:
   ```bash
   export GROQ_API_KEY="your_api_key"
   export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ledgerlens"
   export REDIS_URL="redis://localhost:6379/0"
   ```
4. **Run the API**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 📖 API Usage

### Health Checks
```bash
curl http://localhost:8000/
# Response: {"status": "ok"}
```

### Run an Investigation
The primary endpoint `POST /investigate/` expects a natural language query. 
*(Note: Authentication requires a valid JWT token. For testing, you can use the `create_mock_token` helper in `app/core/security.py`).*

**Request:**
```bash
curl -X POST http://localhost:8000/investigate/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
     -d '{"query": "Why did transaction TXN-102 have a mismatch?"}'
```

**Response:**
```json
{
  "status": "SUCCESS",
  "summary": "Transaction TXN-102 indicates a mismatch between captured cash and recognized revenue.",
  "root_cause": "The payment gateway (Adyen) experienced an insufficient fund capture leading to a $200 discrepancy in the journal entries.",
  "evidence": [
    "{\"id\": \"TXN-102\", \"status\": \"mismatch\", \"metadata\": {\"gateway\": \"Adyen\", \"error\": \"Insufficient fund capture\"}}",
    "{\"transaction_id\": \"TXN-102\", \"total_debit\": 1000.0, \"total_credit\": 1200.0, \"is_balanced\": false}"
  ],
  "confidence": 0.95,
  "tools_used": ["get_transaction", "reconcile_account"]
}
```

---

## 🛠️ Tooling Layer

The agent has strict access to the following deterministic tools based on user roles:
1. `get_transaction`: SQL lookup for basic transaction metadata.
2. `get_payout_details`: Metadata-based payout grouping.
3. `trace_journal_lineage`: Relational lookup of debits and credits.
4. `reconcile_account`: Arithmetic validation of accounting match/mismatch status.
5. `search_tickets_semantic`: Hybrid RAG search (pgvector + FTS) for historical ticket resolutions.

---

## 🧪 Testing and Evaluation

Run the unit tests and the evaluation metric assertions using `pytest`:

```bash
pytest tests/
```

The evaluation framework (`app/eval/metrics.py`) provides quantitative analysis tools:
- **Recall@K:** Effectiveness of vector retrieval.
- **Tool Accuracy:** Jaccard similarity between expected tools vs. agent-selected tools.
- **Grounding Score:** Percentage of expected facts successfully propagated to the final LLM synthesis.

---

## 🛡️ License

This project is licensed under the MIT License.
