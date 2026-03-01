import asyncio
import os
import sys

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine, AsyncSessionLocal
from app.db.models import Base, User, UserRole, Transaction, TransactionStatus, JournalEntry, Ticket, TicketEmbedding

async def init_db():
    print("Initializing DB...")
    # First, configure pgvector
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("pgvector extension ensured.")
        
        # Drop and create tables
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Schema created.")

    async with AsyncSessionLocal() as session:
        # Seed Users
        admin = User(username="admin_user", role=UserRole.ADMIN)
        analyst = User(username="analyst_jane", role=UserRole.ANALYST)
        session.add_all([admin, analyst])
        await session.commit()
        
        # Seed Transactions
        tx1 = Transaction(
            id="TXN-101", 
            user_id=analyst.id, 
            amount=500.0, 
            currency="USD", 
            status=TransactionStatus.COMPLETED,
            metadata_json={"payout_id": "PO-991", "gateway": "Stripe"}
        )
        tx2 = Transaction(
            id="TXN-102", 
            user_id=analyst.id, 
            amount=1200.0, 
            currency="USD", 
            status=TransactionStatus.MISMATCH,
            metadata_json={"payout_id": "PO-992", "gateway": "Adyen", "error": "Insufficient fund capture"}
        )
        session.add_all([tx1, tx2])
        await session.commit()
        
        # Seed Journals
        j1 = JournalEntry(transaction_id=tx1.id, account="Cash", debit=500.0, credit=0.0)
        j2 = JournalEntry(transaction_id=tx1.id, account="Revenue", debit=0.0, credit=500.0)
        
        j3 = JournalEntry(transaction_id=tx2.id, account="Cash", debit=1000.0, credit=0.0) # Notice mismatch
        j4 = JournalEntry(transaction_id=tx2.id, account="Revenue", debit=0.0, credit=1200.0)
        session.add_all([j1, j2, j3, j4])
        await session.commit()
        
        # Seed Tickets
        t1 = Ticket(
            title="Payout Mismatch for Adyen Transactions",
            description="Several transactions via Adyen are showing less cash captured than the revenue recognized.",
            resolution="The payment gateway changed their fee structure unannounced, taking a flat fee before settlement. Update reconciliation logic to account for gateway_fee.",
            status="resolved"
        )
        t2 = Ticket(
            title="Stripe Webhook Delay",
            description="Transactions stuck in pending state for hours.",
            resolution="Redrive webhook events via Stripe dashboard. Add retry logic to webhook consumer.",
            status="resolved"
        )
        session.add_all([t1, t2])
        await session.commit()
        
        # Seed Ticket Embeddings
        # We simulate this for now, normally an embedding model creates this
        simulated_embedding_1 = [0.0] * 384
        simulated_embedding_1[0] = 0.9  # Payout/gateway issue vector
        
        simulated_embedding_2 = [0.0] * 384
        simulated_embedding_2[1] = 0.9  # Webhook/pending issue vector
        
        te1 = TicketEmbedding(ticket_id=t1.id, embedding=simulated_embedding_1)
        te2 = TicketEmbedding(ticket_id=t2.id, embedding=simulated_embedding_2)
        session.add_all([te1, te2])
        
        await session.commit()
        print("Database seeded successfully with sample data!")

if __name__ == "__main__":
    asyncio.run(init_db())
