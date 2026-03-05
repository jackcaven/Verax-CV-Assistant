"""Factory for creating LLM providers."""

from typing import Optional

from verax.llm.base import LLMProvider
from verax.utils import get_logger

logger = get_logger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create(provider_name: str, api_key: Optional[str] = None) -> LLMProvider:
        """Create an LLM provider by name.

        Args:
            provider_name: "openai", "anthropic", or "local"
            api_key: Optional API key (if not provided, uses environment variables)

        Returns:
            LLMProvider instance

        Raises:
            ValueError: If provider name is not recognized
        """
        provider_lower = provider_name.lower()

        if provider_lower == "openai":
            from verax.llm.openai_provider import OpenAIProvider
            logger.debug("Creating OpenAI provider")
            return OpenAIProvider(api_key=api_key)

        elif provider_lower == "anthropic":
            from verax.llm.anthropic_provider import AnthropicProvider
            logger.debug("Creating Anthropic provider")
            return AnthropicProvider(api_key=api_key)

        elif provider_lower == "local":
            from verax.llm.local_provider import LocalProvider
            logger.debug("Creating local (heuristic) provider")
            return LocalProvider()

        else:
            raise ValueError(
                f"Unknown LLM provider: {provider_name}. "
                f"Supported providers: openai, anthropic, local"
            )
