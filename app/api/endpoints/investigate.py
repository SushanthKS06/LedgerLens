from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.core.security import verify_token
# Note: Ensure orchestrator graph uses standard async invokes
from app.agent.orchestrator import investigation_graph

router = APIRouter()

class InvestigateRequest(BaseModel):
    query: str

class InvestigateResponse(BaseModel):
    status: str
    summary: str
    root_cause: str
    evidence: List[str]
    confidence: float
    tools_used: List[str]

@router.post("/", response_model=InvestigateResponse)
async def investigate_endpoint(req: InvestigateRequest, user: dict = Depends(verify_token)):
    user_role = user.get("role", "viewer")
    
    # Initialize state payload
    initial_state = {
        "query": req.query,
        "user_role": user_role,
        "tools_selected": [],
        "evidence": [],
        "errors": []
    }
    
    try:
        # Await graph completion (Multi-step RAG flow)
        final_state = await investigation_graph.ainvoke(initial_state)
        
        resp = final_state.get("final_response")
        if not resp:
            # Fallback if agent failed critically
            raise HTTPException(status_code=500, detail="Investigation failed to produce a structured response.")
            
        return InvestigateResponse(**resp)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error during investigation: {str(e)}")
