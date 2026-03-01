from typing import List

def compute_recall_at_k(retrieved_docs: List[str], relevant_docs: List[str], k: int = 5) -> float:
    """Computes Recall@K for the Vector Retriever components."""
    top_k = retrieved_docs[:k]
    if not relevant_docs:
        return 1.0 # Vacuously true
    hits = sum(1 for doc in relevant_docs if doc in top_k)
    return hits / len(relevant_docs)

def compute_tool_accuracy(used_tools: List[str], expected_tools: List[str]) -> float:
    """Computes Correctness via Jaccard Similarity of Tool Selection."""
    if not expected_tools and not used_tools:
        return 1.0
    if not expected_tools or not used_tools:
        return 0.0
    intersection = set(used_tools).intersection(set(expected_tools))
    union = set(used_tools).union(set(expected_tools))
    return len(intersection) / len(union)

def compute_grounding_score(synthesis: str, evidence: List[str]) -> float:
    """
    Very crude heuristic grounding score.
    Computes percentage of substantial evidence tokens present in final synthesis.
    In real production, this is usually evaluated by another LLM-as-a-Judge.
    """
    if not evidence:
        return 0.0 if synthesis else 1.0
        
    synthesis_lower = synthesis.lower()
    matches = 0
    total_checks = 0
    
    for ev in evidence:
        words = [w for w in ev.split() if len(w) > 5]
        for w in words:
            total_checks += 1
            if w.lower() in synthesis_lower:
                matches += 1
                
    if total_checks == 0:
        return 1.0
    return matches / total_checks
