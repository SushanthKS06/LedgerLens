from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "ok"}
    
@router.get("/metrics")
async def metrics():
    # In a full production setup this would be exposed via prometheus_client
    # For now, we mock standard instrumentation
    return {"requests_total": 0, "errors_total": 0}
