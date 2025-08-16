"""
Centralized configuration for AI models used in the HandyWriterz agent workflow.
This allows for easy updates and management of models for different tasks.
"""

# Model settings for various agent tasks
MODEL_CONFIG = {
    "intent_parser": "chatgpt-5-thinking",
    "planner": "chatgpt-5-thinking",
    "search": {
        "primary": "chatgpt-o3-high",
        "secondary": "sonar-deep",
    },
    "writing": {
        "primary": "gemini-2.5-pro-direct",
        "fallback": "gemini-2.5-pro"
    },
    "evaluation": {
        "primary": "claude-opus-4",
    },
    "orchestration": {
        "strategic_planner": "o3-reasoner",
        "quality_assessor": "claude-opus-4",
        "workflow_optimizer": "gemini-3.0-pro",
        "innovation_catalyst": "claude-sonnet-4",
    },
}

def get_model_config(task: str):
    """
    Retrieves the model configuration for a specific task.

    Args:
        task (str): The task for which to retrieve the model configuration
                    (e.g., "intent_parser", "search", "writing").

    Returns:
        The model configuration for the specified task.
    """
    return MODEL_CONFIG.get(task)
