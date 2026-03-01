from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import List

from app.agent.state import AgentState
from app.agent.llm import get_structured_llm
from app.agent.prompts import INTENT_PROMPT, SYNTHESIS_PROMPT
from app.agent.guardrails import check_rbac, score_confidence, check_abstention

from app.tools.get_transaction import get_transaction, trace_journal_lineage
from app.tools.reconcile import get_payout_details, reconcile_account
from app.tools.search_tickets import search_tickets_semantic

class ToolCallRequest(BaseModel):
    tools: List[dict] = Field(description="List of tools to call. Format: [{'name': 'tool_name', 'args': {'param': 'value'}}]")

class SynthesisResult(BaseModel):
    summary: str
    root_cause: str

async def detect_intent(state: AgentState) -> dict:
    llm = get_structured_llm(ToolCallRequest)
    chain = INTENT_PROMPT | llm
    
    try:
        result = await chain.ainvoke({"query": state["query"]})
        tools_list = result.tools
    except Exception as e:
        return {"errors": [f"Intent detection failed: {str(e)}"], "tools_selected": []}
        
    return {"tools_selected": tools_list, "intent": "detected"}

async def execute_tools(state: AgentState) -> dict:
    evidence = []
    errors = state.get("errors", [])
    
    tools_map = {
        "get_transaction": get_transaction,
        "get_payout_details": get_payout_details,
        "trace_journal_lineage": trace_journal_lineage,
        "reconcile_account": reconcile_account,
        "search_tickets_semantic": search_tickets_semantic
    }
    
    tools_selected = state.get("tools_selected", [])
    if not tools_selected:
        return {"evidence": [], "errors": errors + ["No tools selected."]}
        
    for tc in tools_selected:
        tool_name = tc.get("name")
        args = tc.get("args", {})
        
        # RBAC Check
        if not check_rbac(state.get("user_role", "viewer"), tool_name):
            errors.append(f"RBAC Denied for tool: {tool_name}")
            continue
            
        if tool_name in tools_map:
            func = tools_map[tool_name]
            try:
                res = await func(**args)
                evidence.append(res)
            except Exception as e:
                errors.append(f"Tool {tool_name} failed: {str(e)}")
        else:
            errors.append(f"Unknown tool: {tool_name}")
            
    return {"evidence": evidence, "errors": errors}

async def synthesize_response(state: AgentState) -> dict:
    if not state.get("evidence"):
        return {
            "draft_summary": "No evidence was gathered due to errors or insufficient parameters.", 
            "draft_root_cause": "", 
            "confidence": 0.0
        }
        
    llm = get_structured_llm(SynthesisResult)
    chain = SYNTHESIS_PROMPT | llm
    
    ev_str = "\n".join(state["evidence"])
    try:
        result = await chain.ainvoke({"evidence": ev_str, "query": state["query"]})
        return {"draft_summary": result.summary, "draft_root_cause": result.root_cause}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"Synthesis Error: {str(e)}"]}

async def finalize_guardrails(state: AgentState) -> dict:
    conf = score_confidence(state)
    status = check_abstention(conf)
    
    if state.get("errors"):
        status = "ERROR"
        
    final_resp = {
        "status": status,
        "summary": state.get("draft_summary", ""),
        "root_cause": state.get("draft_root_cause", ""),
        "evidence": state.get("evidence", []),
        "confidence": conf,
        "tools_used": [t.get("name") for t in state.get("tools_selected", [])]
    }
    
    return {"confidence": conf, "status": status, "final_response": final_resp}

def build_investigation_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("execute_tools", execute_tools)
    workflow.add_node("synthesize_response", synthesize_response)
    workflow.add_node("finalize_guardrails", finalize_guardrails)
    
    workflow.set_entry_point("detect_intent")
    workflow.add_edge("detect_intent", "execute_tools")
    workflow.add_edge("execute_tools", "synthesize_response")
    workflow.add_edge("synthesize_response", "finalize_guardrails")
    workflow.add_edge("finalize_guardrails", END)
    
    return workflow.compile()

# Singleton for importing orchestrator into the fast api layer
investigation_graph = build_investigation_graph()
