"""
Admin API endpoints for the new LLM Gateway and Model Policy system.
Extends existing admin functionality with gateway management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from ..auth.admin_auth import require_admin_auth
from ..services.gateway import get_llm_gateway
from ..services.model_policy import get_model_policy_registry, PolicyUpdateMode
from ..services.model_selector import get_model_selector, SelectionStrategy, SelectionTier
from ..services.tracing import get_tracer


admin_gateway_router = APIRouter(prefix="/api/admin/gateway", tags=["admin", "gateway"])


# Pydantic Models for API schemas
class ModelCapabilityResponse(BaseModel):
    """Model capability information"""
    streaming: bool
    function_calling: bool
    vision: bool
    reasoning: bool
    web_search: bool
    long_context: bool
    creative_writing: bool
    code_generation: bool
    json_mode: bool


class ModelPolicyResponse(BaseModel):
    """Model policy information"""
    logical_id: str
    provider: str
    provider_model_id: str
    capabilities: ModelCapabilityResponse
    cost_tier: str
    context_window: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    fallback_models: List[str]
    admin_overridable: bool


class NodeRequirementResponse(BaseModel):
    """Node capability requirements"""
    required_capabilities: List[str]
    preferred_capabilities: List[str]
    min_context_window: int
    max_cost_tier: str
    reasoning_required: bool


class GatewayHealthResponse(BaseModel):
    """Gateway health status"""
    overall_status: str
    providers: Dict[str, Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelPolicyUpdate(BaseModel):
    """Model policy update request"""
    model_id: str
    mode: PolicyUpdateMode = PolicyUpdateMode.OVERRIDE
    ttl: Optional[int] = None


class BulkPolicyUpdate(BaseModel):
    """Bulk policy update request"""
    updates: Dict[str, str]  # node_name -> model_id
    mode: PolicyUpdateMode = PolicyUpdateMode.OVERRIDE


class SelectionContextRequest(BaseModel):
    """Model selection context for testing"""
    node_name: str
    capabilities: List[str] = []
    strategy: SelectionStrategy = SelectionStrategy.BALANCED
    tier: SelectionTier = SelectionTier.STANDARD
    cost_tier_override: Optional[str] = None


class TraceQueryRequest(BaseModel):
    """Trace query parameters"""
    limit: int = Field(50, ge=1, le=500)
    hours: int = Field(1, ge=1, le=168)  # 1 hour to 1 week


# Gateway Status and Health Endpoints
@admin_gateway_router.get("/health", response_model=GatewayHealthResponse)
async def get_gateway_health(admin: dict = Depends(require_admin_auth)):
    """Get overall gateway health status"""
    try:
        gateway = get_llm_gateway()
        health_data = await gateway.health_check()
        
        return GatewayHealthResponse(
            overall_status=health_data["overall_status"],
            providers=health_data["providers"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get gateway health: {str(e)}"
        )


@admin_gateway_router.get("/status")
async def get_gateway_status(admin: dict = Depends(require_admin_auth)):
    """Get detailed gateway status and metrics"""
    try:
        gateway = get_llm_gateway()
        selector = get_model_selector()
        registry = get_model_policy_registry()
        
        health_data = await gateway.health_check()
        validation = await registry.validate_configuration()
        current_assignments = await registry.get_current_assignments()
        
        return {
            "gateway_health": health_data,
            "configuration_valid": validation["valid"],
            "configuration_issues": validation["issues"],
            "configuration_warnings": validation["warnings"],
            "total_policies": validation["total_policies"],
            "total_nodes": validation["total_nodes"],
            "current_assignments": current_assignments,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get gateway status: {str(e)}"
        )


# Model Policy Management Endpoints
@admin_gateway_router.get("/policies", response_model=Dict[str, ModelPolicyResponse])
async def get_all_policies(admin: dict = Depends(require_admin_auth)):
    """Get all model policies"""
    try:
        registry = get_model_policy_registry()
        policies_data = registry.get_all_policies()
        
        # Convert to response models
        policies = {}
        for policy_id, policy_data in policies_data.items():
            policies[policy_id] = ModelPolicyResponse(
                logical_id=policy_data["logical_id"],
                provider=policy_data["provider"],
                provider_model_id=policy_data["provider_model_id"],
                capabilities=ModelCapabilityResponse(**policy_data["capabilities"]),
                cost_tier=policy_data["cost_tier"],
                context_window=policy_data["context_window"],
                input_cost_per_1k=policy_data["input_cost_per_1k"],
                output_cost_per_1k=policy_data["output_cost_per_1k"],
                fallback_models=policy_data["fallback_models"],
                admin_overridable=policy_data["admin_overridable"]
            )
        
        return policies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get policies: {str(e)}"
        )


@admin_gateway_router.get("/node-requirements", response_model=Dict[str, NodeRequirementResponse])
async def get_node_requirements(admin: dict = Depends(require_admin_auth)):
    """Get all node capability requirements"""
    try:
        registry = get_model_policy_registry()
        requirements_data = registry.get_all_node_requirements()
        
        # Convert to response models
        requirements = {}
        for node_name, req_data in requirements_data.items():
            requirements[node_name] = NodeRequirementResponse(
                required_capabilities=req_data["required_capabilities"],
                preferred_capabilities=req_data["preferred_capabilities"],
                min_context_window=req_data["min_context_window"],
                max_cost_tier=req_data["max_cost_tier"],
                reasoning_required=req_data["reasoning_required"]
            )
        
        return requirements
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get node requirements: {str(e)}"
        )


@admin_gateway_router.get("/assignments")
async def get_current_assignments(admin: dict = Depends(require_admin_auth)):
    """Get current model assignments for all nodes"""
    try:
        registry = get_model_policy_registry()
        assignments = await registry.get_current_assignments()
        
        return {
            "assignments": assignments,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assignments: {str(e)}"
        )


# Policy Update Endpoints
@admin_gateway_router.put("/policies/{node_name}")
async def update_node_policy(
    node_name: str,
    update: ModelPolicyUpdate,
    admin: dict = Depends(require_admin_auth)
):
    """Update policy for a specific node"""
    try:
        registry = get_model_policy_registry()
        
        await registry.update_node_policy(
            node_name=node_name,
            model_id=update.model_id,
            mode=update.mode,
            ttl=update.ttl
        )
        
        return {
            "success": True,
            "node_name": node_name,
            "model_id": update.model_id,
            "mode": update.mode,
            "updated_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update policy: {str(e)}"
        )


@admin_gateway_router.put("/policies/bulk")
async def bulk_update_policies(
    update: BulkPolicyUpdate,
    admin: dict = Depends(require_admin_auth)
):
    """Bulk update multiple node policies"""
    try:
        registry = get_model_policy_registry()
        results = await registry.bulk_update_policies(update.updates)
        
        return {
            "results": results,
            "updated_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to bulk update policies: {str(e)}"
        )


@admin_gateway_router.post("/policies/reload")
async def reload_configuration(admin: dict = Depends(require_admin_auth)):
    """Reload model policy configuration from files"""
    try:
        registry = get_model_policy_registry()
        await registry.reload_configuration()
        
        return {
            "success": True,
            "message": "Configuration reloaded successfully",
            "reloaded_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload configuration: {str(e)}"
        )


# Model Selection and Testing Endpoints
@admin_gateway_router.post("/test-selection")
async def test_model_selection(
    context: SelectionContextRequest,
    admin: dict = Depends(require_admin_auth)
):
    """Test model selection for given context"""
    try:
        from ..services.model_selector import SelectionContext, CostLevel
        
        selector = get_model_selector()
        
        # Convert string cost tier to enum if provided
        cost_tier_override = None
        if context.cost_tier_override:
            cost_tier_override = CostLevel(context.cost_tier_override)
        
        selection_context = SelectionContext(
            node_name=context.node_name,
            capabilities=context.capabilities,
            strategy=context.strategy,
            tier=context.tier,
            cost_tier_override=cost_tier_override
        )
        
        result = await selector.select_model(selection_context)
        
        return {
            "selected_model": result.selected_model.logical_id,
            "provider": result.selected_model.provider.value,
            "reasoning": result.reasoning,
            "confidence_score": result.confidence_score,
            "estimated_cost": result.estimated_cost,
            "alternatives": [alt.logical_id for alt in result.alternatives],
            "fallback_chain": result.fallback_chain,
            "tested_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to test model selection: {str(e)}"
        )


@admin_gateway_router.get("/recommendations/{node_name}")
async def get_model_recommendations(
    node_name: str,
    admin: dict = Depends(require_admin_auth)
):
    """Get model recommendations for a specific node"""
    try:
        selector = get_model_selector()
        recommendations = await selector.get_model_recommendations(node_name)
        
        return {
            **recommendations,
            "requested_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@admin_gateway_router.get("/cost-optimization")
async def get_cost_optimization(admin: dict = Depends(require_admin_auth)):
    """Get cost optimization recommendations across all nodes"""
    try:
        selector = get_model_selector()
        optimization = await selector.optimize_fleet_costs()
        
        return {
            **optimization,
            "requested_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cost optimization: {str(e)}"
        )


# Tracing and Monitoring Endpoints
@admin_gateway_router.get("/traces")
async def get_recent_traces(
    query: TraceQueryRequest = Depends(),
    admin: dict = Depends(require_admin_auth)
):
    """Get recent traces for monitoring"""
    try:
        tracer = get_tracer()
        traces = await tracer.get_recent_traces(query.limit)
        
        return {
            "traces": traces,
            "limit": query.limit,
            "requested_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get traces: {str(e)}"
        )


@admin_gateway_router.get("/traces/{trace_id}")
async def get_trace_details(
    trace_id: str,
    admin: dict = Depends(require_admin_auth)
):
    """Get detailed trace information"""
    try:
        tracer = get_tracer()
        trace = await tracer.get_trace(trace_id)
        
        if not trace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trace {trace_id} not found"
            )
        
        return {
            **trace,
            "requested_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trace details: {str(e)}"
        )


@admin_gateway_router.get("/metrics")
async def get_trace_metrics(
    hours: int = Query(1, ge=1, le=168),
    admin: dict = Depends(require_admin_auth)
):
    """Get trace metrics for monitoring"""
    try:
        tracer = get_tracer()
        metrics = await tracer.get_trace_metrics(hours)
        
        return {
            **metrics,
            "requested_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


# Configuration Validation Endpoint
@admin_gateway_router.get("/validate")
async def validate_configuration(admin: dict = Depends(require_admin_auth)):
    """Validate current gateway configuration"""
    try:
        registry = get_model_policy_registry()
        validation = await registry.validate_configuration()
        
        return {
            **validation,
            "validated_by": admin.get("username", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate configuration: {str(e)}"
        )