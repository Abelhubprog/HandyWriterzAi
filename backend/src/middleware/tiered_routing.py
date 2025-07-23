from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict

def select_model(job_size: int, quality_threshold: str) -> Dict[str, str]:
    """
    Selects the appropriate LLM based on job size and user's quality preference.
    """
    if quality_threshold == "high":
        return {"llm": "pro/opus", "embedding": "text-embedding-3-large"}
    
    if job_size > 1500: # words
        return {"llm": "pro/opus", "embedding": "text-embedding-3-large"}
    elif job_size > 500:
        return {"llm": "flash/haiku", "embedding": "text-embedding-3-small"}
    else:
        return {"llm": "flash/haiku", "embedding": "text-embedding-3-small"}

class TieredRoutingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # This middleware would need to be integrated into the request lifecycle
        # before the agent graph is invoked. For now, it's a standalone example.
        
        # A real implementation would parse the request body to get these values.
        job_size = request.scope.get("job_size", 1000) 
        quality_threshold = request.scope.get("quality_threshold", "standard")

        model_map = select_model(job_size, quality_threshold)
        
        # Store the selected models in the request scope to be used by downstream services
        request.scope["model_map"] = model_map
        
        response = await call_next(request)
        return response