from typing import TypedDict, List, Dict, Any, Optional
import operator
from typing_extensions import Annotated

class AgentState(TypedDict):
    """
    State machine payload for the investigation agent.
    """
    query: str
    user_role: str
    
    # Intent Detection
    intent: str
    tools_selected: List[Dict[str, Any]]
    
    # Evidence Gathering
    evidence: List[str]
    
    # Synthesis & Confidence
    draft_summary: str
    draft_root_cause: str
    confidence: float
    
    # Final Output
    status: str # SUCCESS | INSUFFICIENT_EVIDENCE | ERROR
    final_response: Optional[Dict[str, Any]]
    
    # Error tracking
    errors: Annotated[List[str], operator.add]
