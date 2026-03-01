import json
from sqlalchemy.future import select
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.db.models import Ticket
from app.rag.embeddings import get_embedding
from app.rag.cache import get_cached, set_cached

async def retrieve_similar_tickets(query: str, limit: int = 5) -> str:
    """
    Performs Hybrid Retrieval using pgvector (semantic) and PostgreSQL Full Text Search (keyword).
    Results are merged using Reciprocal Rank Fusion (RRF) and cached via Redis.
    """
    # 1. Check Cache
    cache_key = f"rag:{query}:{limit}"
    cached = await get_cached(cache_key)
    if cached:
        return json.dumps(cached)
        
    # 2. Get Embedding
    query_embedding = get_embedding(query)
    
    # 3. Hybrid Search using RRF (Reciprocal Rank Fusion)
    # k = 60 is standard for RRF
    sql = text("""
        WITH semantic_search AS (
            SELECT 
                ticket_id, 
                RANK() OVER (ORDER BY embedding <=> :embedding::vector) as semantic_rank
            FROM ticket_embeddings
            LIMIT 20
        ),
        keyword_search AS (
            SELECT 
                id as ticket_id,
                RANK() OVER (ORDER BY ts_rank_cd(to_tsvector('english', title || ' ' || description), plainto_tsquery('english', :query)) DESC) as keyword_rank
            FROM tickets
            WHERE to_tsvector('english', title || ' ' || description) @@ plainto_tsquery('english', :query)
            LIMIT 20
        )
        SELECT 
            COALESCE(s.ticket_id, k.ticket_id) as ticket_id,
            COALESCE(1.0 / (60 + s.semantic_rank), 0.0) + COALESCE(1.0 / (60 + k.keyword_rank), 0.0) as rrf_score
        FROM semantic_search s
        FULL OUTER JOIN keyword_search k ON s.ticket_id = k.ticket_id
        ORDER BY rrf_score DESC
        LIMIT :limit
    """)
    
    async with AsyncSessionLocal() as session:
        # Convert list of floats to string syntax required by pgvector
        embed_str = f"[{','.join(map(str, query_embedding))}]"
        
        result = await session.execute(sql, {
            "embedding": embed_str,
            "query": query,
            "limit": limit
        })
        
        rows = result.fetchall()
        ticket_ids = [row.ticket_id for row in rows]
        
        if not ticket_ids:
            empty_res = {"query": query, "matches": []}
            await set_cached(cache_key, empty_res, expire=60)
            return json.dumps(empty_res)
            
        # Fetch the actual tickets
        t_stmt = select(Ticket).filter(Ticket.id.in_(ticket_ids))
        t_result = await session.execute(t_stmt)
        tickets = {t.id: t for t in t_result.scalars().all()}
        
        # Preserve sorted RRF order
        output = []
        for tid in ticket_ids:
            t = tickets.get(tid)
            if t:
                output.append({
                    "ticket_id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "resolution": t.resolution,
                    "status": t.status
                })
                
        final_result = {"query": query, "matches": output}
        
        # 4. Cache and return
        await set_cached(cache_key, final_result, expire=300)
        return json.dumps(final_result)
