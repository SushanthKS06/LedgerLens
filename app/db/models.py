import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    MISMATCH = "mismatch"

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(SQLEnum(TransactionStatus), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default={}) # E.g., payout_id, gateway_ref

    journals = relationship("JournalEntry", back_populates="transaction")

class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey('transactions.id'), index=True)
    account = Column(String, index=True, nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="journals")

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    resolution = Column(String, nullable=True)
    status = Column(String, default="open", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class TicketEmbedding(Base):
    __tablename__ = 'ticket_embeddings'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    # Using 384 dimensions typical for standard lightweight OS embedding models (e.g. all-MiniLM-L6-v2)
    embedding = Column(Vector(384))

# Indexes for pgvector
Index('ix_ticket_embeddings_embedding_hnsw', 
      TicketEmbedding.embedding, 
      postgresql_using='hnsw', 
      postgresql_with={'m': 16, 'ef_construction': 64}, 
      postgresql_ops={'embedding': 'vector_cosine_ops'})
