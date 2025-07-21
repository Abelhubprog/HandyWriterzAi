"""
Admin API endpoints for model configuration management
Provides RESTful endpoints for the Pluggable-Model control panel
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from src.services.model_service import get_model_service
from src.services.security_service import require_authorization

logger = logging.getLogger(__name__)

# Create router for admin model management
router = APIRouter(prefix="/api/admin/models", tags=["admin", "models"])


class ModelUpdateRequest(BaseModel):
    """Request model for updating agent model configuration"""
    agent_name: str
    new_model: str
    reason: Optional[str] = None


class BulkModelUpdateRequest(BaseModel):
    """Request model for bulk model updates"""
    updates: List[Dict[str, str]]  # List of {"agent_name": "new_model"}
    reason: Optional[str] = None


class SwarmConfigUpdateRequest(BaseModel):
    """Request model for updating swarm configuration"""
    swarm_name: str
    agent_configs: Dict[str, Dict[str, Any]]
    consensus_threshold: Optional[float] = None
    diversity_target: Optional[float] = None


@router.get("/config/summary")
async def get_config_summary(
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Get a summary of the current model configuration"""
    try:
        model_service = get_model_service()
        summary = model_service.get_config_summary()
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get config summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve configuration summary: {str(e)}"
        )


@router.get("/agents")
async def list_agents(
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Get list of all configured agents with their current models"""
    try:
        model_service = get_model_service()
        agents = await model_service.get_agent_list()
        
        return {
            "success": True,
            "data": {
                "agents": agents,
                "total_count": len(agents)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent list: {str(e)}"
        )


@router.get("/agents/{agent_name}")
async def get_agent_config(
    agent_name: str,
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Get detailed configuration for a specific agent"""
    try:
        model_service = get_model_service()
        agent_config = await model_service.get_agent_config(agent_name)
        
        if not agent_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found"
            )
        
        # Get metrics for this agent
        metrics = await model_service.get_model_metrics(agent_name)
        
        return {
            "success": True,
            "data": {
                "config": {
                    "name": agent_config.name,
                    "description": agent_config.description,
                    "model": agent_config.model,
                    "fallback_models": agent_config.fallback_models,
                    "temperature": agent_config.temperature,
                    "max_tokens": agent_config.max_tokens,
                    "timeout_seconds": agent_config.timeout_seconds,
                    "parameters": agent_config.parameters
                },
                "metrics": metrics
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent config for {agent_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent configuration: {str(e)}"
        )


@router.put("/agents/{agent_name}/model")
async def update_agent_model(
    agent_name: str,
    request: ModelUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Update the model for a specific agent"""
    try:
        model_service = get_model_service()
        
        # Validate that the agent exists
        agent_config = await model_service.get_agent_config(agent_name)
        if not agent_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found"
            )
        
        # Validate that the new model is available
        available_models = await model_service.get_available_models()
        all_models = []
        for provider_models in available_models.values():
            all_models.extend(provider_models)
        
        if request.new_model not in all_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model '{request.new_model}' is not available. Available models: {all_models}"
            )
        
        # Update the model
        success = await model_service.update_agent_model(agent_name, request.new_model)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update agent model"
            )
        
        logger.info(f"Admin {current_user.get('wallet_address', 'unknown')} updated {agent_name} model: {agent_config.model} -> {request.new_model}")
        
        return {
            "success": True,
            "data": {
                "agent_name": agent_name,
                "old_model": agent_config.model,
                "new_model": request.new_model,
                "reason": request.reason,
                "updated_by": current_user.get('wallet_address', 'unknown'),
                "updated_at": datetime.utcnow().isoformat()
            },
            "message": f"Successfully updated {agent_name} model to {request.new_model}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent model: {str(e)}"
        )


@router.put("/agents/bulk-update")
async def bulk_update_models(
    request: BulkModelUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Update multiple agent models in bulk"""
    try:
        model_service = get_model_service()
        results = []
        errors = []
        
        # Validate all models first
        available_models = await model_service.get_available_models()
        all_models = []
        for provider_models in available_models.values():
            all_models.extend(provider_models)
        
        for update in request.updates:
            agent_name = update.get("agent_name")
            new_model = update.get("new_model")
            
            if not agent_name or not new_model:
                errors.append(f"Invalid update: {update}")
                continue
            
            # Check if agent exists
            agent_config = await model_service.get_agent_config(agent_name)
            if not agent_config:
                errors.append(f"Agent '{agent_name}' not found")
                continue
            
            # Check if model is available
            if new_model not in all_models:
                errors.append(f"Model '{new_model}' not available for agent '{agent_name}'")
                continue
            
            # Perform update
            success = await model_service.update_agent_model(agent_name, new_model)
            
            if success:
                results.append({
                    "agent_name": agent_name,
                    "old_model": agent_config.model,
                    "new_model": new_model,
                    "status": "success"
                })
                logger.info(f"Bulk update: {agent_name} model changed to {new_model}")
            else:
                errors.append(f"Failed to update {agent_name} to {new_model}")
        
        return {
            "success": len(errors) == 0,
            "data": {
                "successful_updates": results,
                "errors": errors,
                "total_attempted": len(request.updates),
                "successful_count": len(results),
                "error_count": len(errors),
                "updated_by": current_user.get('wallet_address', 'unknown'),
                "updated_at": datetime.utcnow().isoformat(),
                "reason": request.reason
            },
            "message": f"Bulk update completed: {len(results)} successful, {len(errors)} errors"
        }
        
    except Exception as e:
        logger.error(f"Bulk model update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk model update failed: {str(e)}"
        )


@router.get("/providers")
async def list_providers(
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Get list of all available model providers and their models"""
    try:
        model_service = get_model_service()
        available_models = await model_service.get_available_models()
        
        return {
            "success": True,
            "data": {
                "providers": available_models,
                "total_providers": len(available_models),
                "total_models": sum(len(models) for models in available_models.values())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve provider list: {str(e)}"
        )


@router.get("/metrics")
async def get_model_metrics(
    agent_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Get performance metrics for models"""
    try:
        model_service = get_model_service()
        metrics = await model_service.get_model_metrics(agent_name)
        
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "agent_filter": agent_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get model metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model metrics: {str(e)}"
        )


@router.get("/swarms")
async def list_swarm_configs(
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Get list of all swarm intelligence configurations"""
    try:
        model_service = get_model_service()
        
        # Get all swarm configurations
        qa_swarm = await model_service.get_swarm_config("qa_swarm")
        research_swarm = await model_service.get_swarm_config("research_swarm")
        writing_swarm = await model_service.get_swarm_config("writing_swarm")
        
        swarms = {}
        if qa_swarm:
            swarms["qa_swarm"] = qa_swarm
        if research_swarm:
            swarms["research_swarm"] = research_swarm
        if writing_swarm:
            swarms["writing_swarm"] = writing_swarm
        
        return {
            "success": True,
            "data": {
                "swarms": swarms,
                "total_swarms": len(swarms)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list swarm configs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve swarm configurations: {str(e)}"
        )


@router.post("/reload")
async def reload_configuration(
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Force reload of model configuration from file"""
    try:
        model_service = get_model_service()
        reloaded = model_service.reload_config()
        
        if reloaded:
            logger.info(f"Configuration reloaded by admin: {current_user.get('wallet_address', 'unknown')}")
            message = "Configuration successfully reloaded from file"
        else:
            message = "Configuration was already up to date"
        
        return {
            "success": True,
            "data": {
                "reloaded": reloaded,
                "config_summary": model_service.get_config_summary(),
                "reloaded_by": current_user.get('wallet_address', 'unknown'),
                "reloaded_at": datetime.utcnow().isoformat()
            },
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload configuration: {str(e)}"
        )


@router.get("/health")
async def model_service_health(
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Check health of model service and configurations"""
    try:
        model_service = get_model_service()
        
        # Test a few agent configurations
        test_agents = ["search_claude", "search_gemini", "writer"]
        agent_statuses = {}
        
        for agent_name in test_agents:
            try:
                config = await model_service.get_agent_config(agent_name)
                if config:
                    agent_statuses[agent_name] = {
                        "status": "healthy",
                        "model": config.model,
                        "fallback_count": len(config.fallback_models)
                    }
                else:
                    agent_statuses[agent_name] = {
                        "status": "missing_config",
                        "model": None
                    }
            except Exception as e:
                agent_statuses[agent_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        overall_health = "healthy" if all(
            status["status"] == "healthy" for status in agent_statuses.values()
        ) else "degraded"
        
        return {
            "success": True,
            "data": {
                "overall_health": overall_health,
                "agent_statuses": agent_statuses,
                "config_summary": model_service.get_config_summary(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Model service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )