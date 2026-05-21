from typing import Optional
from .base import AIAdapter
from .mock_adapter import MockAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .gemini_adapter import GeminiAdapter
from ..config import settings

def get_adapter(provider_name: Optional[str] = None, api_key: Optional[str] = None) -> AIAdapter:
    """
    Factory function to instantiate the requested AIAdapter.
    Defaults to settings.DEFAULT_PROVIDER if not specified.
    """
    target_provider = (provider_name or settings.DEFAULT_PROVIDER).lower()
    
    if target_provider == "mock":
        return MockAdapter()
    elif target_provider == "openai":
        return OpenAIAdapter(api_key=api_key)
    elif target_provider == "anthropic":
        return AnthropicAdapter(api_key=api_key)
    elif target_provider == "gemini":
        return GeminiAdapter(api_key=api_key)
    else:
        raise ValueError(f"Unsupported provider: {target_provider}")
