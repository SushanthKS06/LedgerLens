from fastapi import FastAPI
from app.api.endpoints import investigate, health

app = FastAPI(
    title="LedgerLens Investigation API",
    description="Production-ready multi-step RAG for forensic financial investigations.",
    version="1.0.0"
)

# Includes
app.include_router(health.router, tags=["health"])
app.include_router(investigate.router, prefix="/investigate", tags=["investigate"])

# Global Exception Handlers can be added here
