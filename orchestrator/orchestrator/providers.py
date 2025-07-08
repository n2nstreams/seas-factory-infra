import os
from typing import Any

# Provider selection based on environment variable
PROVIDER = os.getenv("MODEL_PROVIDER", "gemini").lower()

def get_llm_model() -> str:
    """
    Returns the appropriate model string based on the provider selection.
    
    Returns:
        str: Model identifier for the selected provider
    """
    if PROVIDER == "gpt4o":
        # Use GPT-4o model
        return "gpt-4o-mini"
    elif PROVIDER == "openai":
        # Alternative alias for OpenAI
        return "gpt-4o-mini"
    else:
        # Default to Gemini 2.5 Pro
        return "gemini-2.0-flash"

def get_provider_config() -> dict:
    """
    Returns provider-specific configuration.
    
    Returns:
        dict: Configuration for the selected provider
    """
    config = {
        "provider": PROVIDER,
        "model": get_llm_model()
    }
    
    if PROVIDER in ["gpt4o", "openai"]:
        # OpenAI requires API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
        config["api_key"] = api_key
    
    return config

def validate_provider_config() -> bool:
    """
    Validates that the current provider configuration is valid.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    try:
        config = get_provider_config()
        return True
    except ValueError:
        return False 