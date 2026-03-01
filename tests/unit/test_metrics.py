from app.eval.metrics import compute_recall_at_k, compute_tool_accuracy, compute_grounding_score

def test_recall_at_k():
    assert compute_recall_at_k(["A", "B", "C"], ["B"], k=2) == 1.0
    assert compute_recall_at_k(["A", "C", "D"], ["B"], k=2) == 0.0

def test_tool_accuracy():
    assert compute_tool_accuracy(["get_transaction", "reconcile_account"], ["get_transaction", "search_tickets"]) == 0.3333333333333333
    assert compute_tool_accuracy(["get_transaction"], ["get_transaction"]) == 1.0

def test_grounding_score():
    evidence = ["The transaction TXN-102 failed due to an Adyen gateway mismatch."]
    synthesis_good = "The root cause is a gateway mismatch at Adyen for TXN-102."
    synthesis_bad = "It was a random error from Stripe."
    
    # 4 distinct large words (>5 chars): transaction, TXN-102, failed, gateway, mismatch
    assert compute_grounding_score(synthesis_good, evidence) > 0.0
    assert compute_grounding_score(synthesis_bad, evidence) == 0.0
