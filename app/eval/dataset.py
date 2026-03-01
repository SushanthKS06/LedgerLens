from pydantic import BaseModel
from typing import List

class EvalTestCase(BaseModel):
    query: str
    expected_tools: List[str]
    expected_grounding_docs: List[str]
    expected_root_cause_keywords: List[str]

# Golden Dataset example for tests
eval_dataset = [
    EvalTestCase(
        query="Why did transaction TXN-102 have a discrepancy?",
        expected_tools=["get_transaction", "reconcile_account", "trace_journal_lineage"],
        expected_grounding_docs=["TXN-102", "Adyen"],
        expected_root_cause_keywords=["mismatch", "fee", "gateway"]
    ),
    EvalTestCase(
        query="What happened with the pending Stripe payouts yesterday?",
        expected_tools=["search_tickets_semantic"],
        expected_grounding_docs=["Stripe Webhook Delay"],
        expected_root_cause_keywords=["delay", "webhook", "pending"]
    )
]
