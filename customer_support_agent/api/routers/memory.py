"""Customer memory routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from customer_support_agent.api.dependencies import (
    get_copilot_or_503,
    get_customers_repository,
)
from customer_support_agent.repos.sqlite.customers import CustomerRepository
from customer_support_agent.schemas.api import CustomerMemoriesResponse, CustomerMemorySearchResponse
from customer_support_agent.services.copilot_service import SupportCopilot

router = APIRouter()

@router.get("/api/customers/{customer_id}/memories", response_model=CustomerMemoriesResponse)
def customer_memories_route(
    customer_id: int,
    customers_repo: CustomerRepository = Depends(get_customers_repository),
    copilot: SupportCopilot = Depends(get_copilot_or_503)
) -> dict:
    customer = customers_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        memories = copilot.list_customer_memories(
            customer_email=customer["email"],
            customer_company=customer.get("company")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load memories: {e}")
    
    return {
        "customer_id": customer_id,
        "customer_email": customer["email"],
        "memories": memories
    }

@router.get("/api/customers/{customer_id}/memory-search", response_model=CustomerMemorySearchResponse)
def customer_memory_search_route(
    customer_id: int,
    query: str,
    limit: int = 10,
    customers_repo: CustomerRepository = Depends(get_customers_repository),
    copilot: SupportCopilot = Depends(get_copilot_or_503)
) -> dict:
    customer = customers_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        results = copilot.search_customer_memories(
            customer_email = customer["email"],
            query = query,
            customer_company = customer.get("company"),
            limit = max(1, min(limit, 25))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {e}")
    
    return {
        "customer_id": customer_id,
        "customer_email": customer["email"],
        "query": query,
        "results": results
    }
        
    
    


