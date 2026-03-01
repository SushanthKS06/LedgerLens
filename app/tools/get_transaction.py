import json
from pydantic import BaseModel, ValidationError
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.db.models import Transaction, JournalEntry

class SingleStringInput(BaseModel):
    id: str

async def get_transaction(transaction_id: str) -> str:
    """Gets details of a single transaction."""
    try:
        SingleStringInput(id=transaction_id)
    except ValidationError as e:
        return json.dumps({"error": "Invalid input", "details": e.errors()})
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Transaction).filter(Transaction.id == transaction_id))
        tx = result.scalar_one_or_none()
        if tx:
            return json.dumps({
                "id": tx.id,
                "amount": tx.amount,
                "currency": tx.currency,
                "status": tx.status.value,
                "timestamp": tx.timestamp.isoformat(),
                "metadata": tx.metadata_json
            })
        return json.dumps({"error": "Transaction not found"})

async def trace_journal_lineage(transaction_id: str) -> str:
    """Gets all journal entries connected to a transaction ID."""
    try:
        SingleStringInput(id=transaction_id)
    except ValidationError as e:
        return json.dumps({"error": "Invalid input", "details": e.errors()})
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(JournalEntry).filter(JournalEntry.transaction_id == transaction_id))
        journals = result.scalars().all()
        if not journals:
            return json.dumps({"error": f"No journal entries found for transaction {transaction_id}"})
        
        output = []
        for j in journals:
            output.append({
                "id": j.id,
                "account": j.account,
                "debit": j.debit,
                "credit": j.credit,
                "timestamp": j.timestamp.isoformat()
            })
        return json.dumps({"transaction_id": transaction_id, "journal_entries": output})
