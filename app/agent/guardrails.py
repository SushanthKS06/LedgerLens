import json
from app.agent.state import AgentState

def check_rbac(role: str, tool_name: str) -> bool:
    """Enforce strictly declarative Role Based Access Control on Tools."""
    allowed = {
        "admin": ["get_transaction", "get_payout_details", "trace_journal_lineage", "reconcile_account", "search_tickets_semantic"],
        "analyst": ["get_transaction", "get_payout_details", "trace_journal_lineage", "reconcile_account", "search_tickets_semantic"],
        "viewer": ["search_tickets_semantic"]
    }
    return tool_name in allowed.get(role.lower(), [])

def score_confidence(state: AgentState) -> float:
    """
    Computes confidence (0.0 - 1.0) based on evidence existence constraint validations.
    """
    if not state.get("evidence"):
        return 0.0
        
    valid_evidence = 0
    total_evidence = len(state["evidence"])
    
    for ev in state["evidence"]:
        try:
            parsed = json.loads(ev)
            if "error" not in parsed:
                valid_evidence += 1
        except:
            pass
            
    if valid_evidence == 0:
        return 0.2
        
    # Minimum confidence to proceed if all returned successfully is 0.7 
    # Scaled up slightly for amount of valid evidence vs total tools
    ratio = valid_evidence / total_evidence
    confidence = 0.5 + (0.45 * ratio)
    
    return round(min(1.0, confidence), 2)

def check_abstention(confidence: float) -> str:
    """Determines operation status based on confidence levels."""
    if confidence < 0.6:
        return "INSUFFICIENT_EVIDENCE"
    return "SUCCESS"
