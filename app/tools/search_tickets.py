import json
from pydantic import BaseModel, ValidationError
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.db.models import Ticket, TicketEmbedding
from app.rag.embeddings import get_embedding

class SearchInput(BaseModel):
    query: str
    limit: int = 3

async def search_tickets_semantic(query: str, limit: int = 3) -> str:
    """Uses semantic similarity to find relevant resolved tickets in history."""
    try:
        SearchInput(query=query, limit=limit)
    except ValidationError as e:
        return json.dumps({"error": "Invalid input", "details": e.errors()})
        
    query_embedding = get_embedding(query)
    
    async with AsyncSessionLocal() as session:
        # Use cosine distance across pgvector via L2 or Cosine. (<=> is Cosine distance in pgvector)
        # SQLAlchemy syntax for pgvector
        stmt = select(TicketEmbedding).order_by(
            TicketEmbedding.embedding.cosine_distance(query_embedding)
        ).limit(limit)
        
        result = await session.execute(stmt)
        ticket_embeds = result.scalars().all()
        
        if not ticket_embeds:
            return json.dumps({"error": "No records found", "results": []})
            
        # Join to get the actual tickets
        ticket_ids = [te.ticket_id for te in ticket_embeds]
        
        t_stmt = select(Ticket).filter(Ticket.id.in_(ticket_ids))
        t_result = await session.execute(t_stmt)
        tickets = {t.id: t for t in t_result.scalars().all()}
        
        output = []
        for te in ticket_embeds:
            t = tickets.get(te.ticket_id)
            if t:
                output.append({
                    "ticket_id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "resolution": t.resolution,
                    "status": t.status
                })
                
        return json.dumps({"query": query, "matches": output})
