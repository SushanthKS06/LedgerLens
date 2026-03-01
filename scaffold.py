import os
from pathlib import Path

def scaffold():
    base = Path("d:/NthgButProjects/LedgerLens")
    directories = [
        "app/api/endpoints",
        "app/core",
        "app/db/migrations",
        "app/models",
        "app/schemas",
        "app/services",
        "app/tools",
        "app/rag",
        "app/agent",
        "app/eval",
        "tests/unit",
        "tests/integration",
        "tests/agent",
        "docker",
        "scripts"
    ]
    files = [
        ("app/__init__.py", ""),
        ("app/main.py", ""),
        ("app/api/__init__.py", ""),
        ("app/api/endpoints/__init__.py", ""),
        ("app/api/endpoints/investigate.py", ""),
        ("app/api/endpoints/health.py", ""),
        ("app/api/dependencies.py", ""),
        ("app/core/__init__.py", ""),
        ("app/core/config.py", ""),
        ("app/core/security.py", ""),
        ("app/core/exceptions.py", ""),
        ("app/db/__init__.py", ""),
        ("app/db/session.py", ""),
        ("app/db/models.py", ""),
        ("app/db/vector_store.py", ""),
        ("app/models/__init__.py", ""),
        ("app/schemas/__init__.py", ""),
        ("app/schemas/investigation.py", ""),
        ("app/services/__init__.py", ""),
        ("app/tools/__init__.py", ""),
        ("app/tools/get_transaction.py", ""),
        ("app/tools/get_payout.py", ""),
        ("app/tools/trace_journal.py", ""),
        ("app/tools/reconcile.py", ""),
        ("app/rag/__init__.py", ""),
        ("app/rag/embeddings.py", ""),
        ("app/rag/retriever.py", ""),
        ("app/rag/cache.py", ""),
        ("app/agent/__init__.py", ""),
        ("app/agent/orchestrator.py", ""),
        ("app/agent/state.py", ""),
        ("app/agent/prompts.py", ""),
        ("app/agent/guardrails.py", ""),
        ("app/eval/__init__.py", ""),
        ("app/eval/metrics.py", ""),
        ("app/eval/dataset.py", ""),
        ("docker/Dockerfile", ""),
        ("docker/docker-compose.yml", ""),
        ("requirements.txt", ""),
        (".env.example", ""),
        ("README.md", "# LedgerLens - AI Investigation System\n")
    ]
    
    for d in directories:
        (base / d).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {d}")
    
    for f, content in files:
        filepath = base / f
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
            print(f"Created file: {f}")
        else:
            print(f"File already exists: {f}")

    print("\nPhase 2 Complete: Project Structure Generated successfully.")

if __name__ == "__main__":
    scaffold()
