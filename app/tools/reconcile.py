import json
from pydantic import BaseModel, ValidationError
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.db.models import Transaction, JournalEntry

class SingleStringInput(BaseModel):
    id: str

async def get_payout_details(payout_id: str) -> str:
    """Finds all transactions belonging to a specific payout ID via metadata_json scan."""
    try:
        SingleStringInput(id=payout_id)
    except ValidationError as e:
        return json.dumps({"error": "Invalid input", "details": e.errors()})
        
    async with AsyncSessionLocal() as session:
        # Note: postgres JSONB path operator or generic json filter. 
        # Using string matching inside JSON if text-based json is used, or a crude scan for simplicity if standard JSON column.
        # Safe way in SQLAlchemy JSON:
        result = await session.execute(
            select(Transaction).filter(Transaction.metadata_json["payout_id"].as_string() == payout_id)
        )
        txs = result.scalars().all()
        if not txs:
            return json.dumps({"error": f"No transactions found for payout {payout_id}"})
        
        output = []
        for tx in txs:
            output.append({
                "id": tx.id,
                "amount": tx.amount,
                "currency": tx.currency,
                "status": tx.status.value
            })
        return json.dumps({"payout_id": payout_id, "transactions": output})

async def reconcile_account(transaction_id: str) -> str:
    """Reconciles debits and credits of a transaction to check for imbalance."""
    try:
        SingleStringInput(id=transaction_id)
    except ValidationError as e:
        return json.dumps({"error": "Invalid input", "details": e.errors()})
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(JournalEntry).filter(JournalEntry.transaction_id == transaction_id))
        journals = result.scalars().all()
        
        if not journals:
            return json.dumps({"error": f"No journals found to reconcile for transaction {transaction_id}"})
            
        total_debit = sum(j.debit for j in journals)
        total_credit = sum(j.credit for j in journals)
        diff = total_debit - total_credit
        
        is_balanced = abs(diff) < 0.001
        
        return json.dumps({
            "transaction_id": transaction_id,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "diff_amount": diff,
            "is_balanced": is_balanced,
            "status": "BALANCED" if is_balanced else "MISMATCH"
        })
