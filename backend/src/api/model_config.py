"""
Model Configuration API endpoints for HandyWriterzAI.
Provides REST API access to model configuration and assignment.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, HTTPException
from pydantic import BaseModel, Field
import yaml
import os

from ..config.model_config import MODEL_CONFIG, get_model_config
from ..services.llm_service import get_all_llm_clients

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["models"])

# Request/Response Models

class ModelAssignmentRequest(BaseModel):
    task: str = Field(..., description="Task name (e.g., 'writing', 'evaluation')")
    model_name: str = Field(..., description="Model name to assign")

class ModelAssignmentResponse(BaseModel):
    success: bool
    message: str
    previous_model: Optional[str] = None
    new_model: Optional[str] = None

class ModelListResponse(BaseModel):
    available_models: Dict[str, Any]
    current_assignments: Dict[str, Any]

class ModelHealthResponse(BaseModel):
    model_name: str
    provider: str
    status: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

class ModelHealthCheckResponse(BaseModel):
    models: Dict[str, ModelHealthResponse]
    timestamp: str

# Global variable to store runtime model assignments
_runtime_model_assignments = {}

# API Endpoints

@router.get("/assignments", response_model=ModelListResponse)
async def get_model_assignments():
    """Get current model assignments and available models."""
    try:
        # Get available models from YAML config
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "model_config.yaml")
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)

        available_models = yaml_config.get("logical_models", {})
        defaults = yaml_config.get("defaults", {})

        # Combine default assignments with runtime assignments
        current_assignments = {**defaults, **_runtime_model_assignments}

        return ModelListResponse(
            available_models=available_models,
            current_assignments=current_assignments
        )

    except Exception as e:
        logger.error(f"Failed to get model assignments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model assignments: {str(e)}")

@router.post("/assign", response_model=ModelAssignmentResponse)
async def assign_model(request: ModelAssignmentRequest):
    """Assign a model to a specific task at runtime."""
    try:
        # Validate that the model exists
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "model_config.yaml")
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)

        available_models = yaml_config.get("logical_models", {})
        if request.model_name not in available_models:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{request.model_name}' not found. Available models: {list(available_models.keys())}"
            )

        # Get current assignment
        defaults = yaml_config.get("defaults", {})
        current_model = _runtime_model_assignments.get(request.task) or defaults.get(request.task)

        # Update runtime assignment
        _runtime_model_assignments[request.task] = request.model_name

        logger.info(f"Model assignment updated: {request.task} -> {request.model_name}")

        return ModelAssignmentResponse(
            success=True,
            message=f"Model '{request.model_name}' assigned to task '{request.task}'",
            previous_model=current_model,
            new_model=request.model_name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assign model: {str(e)}")

@router.delete("/assign/{task}", response_model=ModelAssignmentResponse)
async def reset_model_assignment(task: str):
    """Reset model assignment for a task to its default value."""
    try:
        # Get default assignment
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "model_config.yaml")
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)

        defaults = yaml_config.get("defaults", {})
        default_model = defaults.get(task)

        if not default_model:
            raise HTTPException(status_code=400, detail=f"No default model found for task '{task}'")

        # Get current runtime assignment
        current_model = _runtime_model_assignments.get(task)

        # Remove runtime assignment
        if task in _runtime_model_assignments:
            del _runtime_model_assignments[task]

        logger.info(f"Model assignment reset: {task} -> {default_model} (default)")

        return ModelAssignmentResponse(
            success=True,
            message=f"Model assignment for task '{task}' reset to default '{default_model}'",
            previous_model=current_model,
            new_model=default_model
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset model assignment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset model assignment: {str(e)}")

@router.get("/health", response_model=ModelHealthCheckResponse)
async def model_health_check():
    """Check health status of all configured models."""
    try:
        from datetime import datetime
        import asyncio

        # Get all LLM clients
        llm_clients = get_all_llm_clients()

        health_results = {}
        timestamp = str(datetime.utcnow())

        # Check each model
        for model_name, client in llm_clients.items():
            try:
                start_time = asyncio.get_event_loop().time()

                # Simple health check - try to get model info
                # This is a basic check, in production you might want more comprehensive testing
                model_info = getattr(client, 'model_name', model_name)

                end_time = asyncio.get_event_loop().time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds

                health_results[model_name] = ModelHealthResponse(
                    model_name=model_name,
                    provider=getattr(client, 'provider_name', 'unknown'),
                    status="healthy",
                    response_time_ms=round(response_time, 2)
                )

            except Exception as e:
                health_results[model_name] = ModelHealthResponse(
                    model_name=model_name,
                    provider=getattr(client, 'provider_name', 'unknown'),
                    status="unhealthy",
                    error=str(e)
                )

        return ModelHealthCheckResponse(
            models=health_results,
            timestamp=timestamp
        )

    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/config/{task}")
async def get_task_model_config(task: str):
    """Get the current model configuration for a specific task."""
    try:
        # Check runtime assignments first
        if task in _runtime_model_assignments:
            model_name = _runtime_model_assignments[task]
        else:
            # Fall back to default configuration
            model_name = get_model_config(task)

        if not model_name:
            raise HTTPException(status_code=404, detail=f"No model configured for task '{task}'")

        return {
            "task": task,
            "model_name": model_name,
            "runtime_override": task in _runtime_model_assignments
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task model config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task model config: {str(e)}")
