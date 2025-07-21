"""
Centralized configuration for AI models used in the HandyWriterz agent workflow.
This allows for easy updates and management of models for different tasks.
"""

# Model settings for various agent tasks
MODEL_CONFIG = {
    "intent_parser": "gemini-2.5-pro",
    "planner": "gemini-2.5-pro",
    "search": {
        "primary": "perplexity",
        "secondary": "gemini-2.5-pro",
    },
    "writing": {
        "primary": "gemini-2.5-pro",
        "fallback": "gemini-2.0-pro"
    },
    "evaluation": {
        "primary": "gemini-2.5-pro",
    },
    "orchestration": {
        "strategic_planner": "gemini-2.5-pro",
        "quality_assessor": "gemini-2.5-pro",
        "workflow_optimizer": "gemini-2.5-pro",
        "innovation_catalyst": "gemini-2.5-pro",
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
