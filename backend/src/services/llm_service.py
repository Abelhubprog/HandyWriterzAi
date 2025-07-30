import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from src.config.model_config import get_model_config

def get_llm_client(task: str = "default", model_preference: str = None):
    """
    Returns a LangChain LLM client based on the task and model preference.
    """
    model_config = get_model_config(task)
    
    if model_preference:
        model_name = model_preference
    elif isinstance(model_config, str):
        model_name = model_config
    elif isinstance(model_config, dict):
        model_name = model_config.get("primary")
    else:
        model_name = "gemini-1.5-pro-latest"  # Default model

    if "gemini" in model_name:
        return ChatGoogleGenerativeAI(model=model_name, api_key=os.getenv("GEMINI_API_KEY"))
    elif "grok" in model_name:
        return ChatGroq(model=model_name, api_key=os.getenv("GROQ_API_KEY"))
    elif "claude" in model_name:
        return ChatAnthropic(model=model_name, api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif "openai" in model_name or "gpt" in model_name:
        return ChatOpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"))
    else:  # Default to Gemini
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=os.getenv("GEMINI_API_KEY"))

def get_all_llm_clients() -> dict:
    """
    Instantiates and returns a dictionary of all available LLM clients.
    """
    clients = {}
    # This could be driven by a more dynamic config, but for now, we'll hardcode the main ones.
    model_map = {
        "gemini": ("gemini-1.5-pro-latest", "GEMINI_API_KEY", ChatGoogleGenerativeAI),
        "openai": ("gpt-4o", "OPENAI_API_KEY", ChatOpenAI),
        "claude": ("claude-3-5-sonnet-20240620", "ANTHROPIC_API_KEY", ChatAnthropic),
        "grok": ("llama3-70b-8192", "GROQ_API_KEY", ChatGroq),
    }

    for name, (model, key, client_class) in model_map.items():
        api_key = os.getenv(key)
        if api_key:
            clients[name] = client_class(model=model, api_key=api_key)
            
    return clients
