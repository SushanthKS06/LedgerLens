import os
from langchain_groq import ChatGroq
from tenacity import retry, stop_after_attempt, wait_exponential

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "mock_key")

def get_base_llm():
    """
    Configures and returns the base Groq LLM 
    with timeout and rate limit optimizations.
    """
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,  # Deterministic behavior
        api_key=GROQ_API_KEY,
        max_retries=3,
        timeout=30.0
    )

def get_structured_llm(schema):
    """Returns an LLM forced to output a specific Pydantic schema."""
    llm = get_base_llm()
    return llm.with_structured_output(schema)

# Tenacity resilient execution wrapper for raw LLM calls if needed
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def resilient_llm_call(prompt_messages):
    llm = get_base_llm()
    return await llm.ainvoke(prompt_messages)
