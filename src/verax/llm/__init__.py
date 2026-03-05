"""LLM providers for Verax."""

from verax.llm.base import LLMProvider
from verax.llm.factory import LLMProviderFactory
from verax.llm.local_provider import LocalProvider

# Note: OpenAI and Anthropic providers are lazy-loaded by factory
# to avoid import errors if dependencies not installed

__all__ = [
    "LLMProvider",
    "LLMProviderFactory",
    "LocalProvider",
]
