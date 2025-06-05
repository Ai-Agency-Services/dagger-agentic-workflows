from typing import NamedTuple, Optional

import dagger
from dagger import function, object_type


@object_type
class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: dagger.Secret


@object_type
class DaggerAgentsUtils:
    """Utility class for Dagger agents"""

    @function
    async def get_llm_credentials(
        provider: str,
        open_router_key: Optional[dagger.Secret],
        openai_key: Optional[dagger.Secret],
    ) -> LLMCredentials:
        """
        Determines the LLM base URL and retrieves the plaintext API key based on the provider.

        Args:
            provider: The name of the LLM provider ('openrouter' or 'openai').
            open_router_key: The Dagger secret for the OpenRouter API key.
            openai_key: The Dagger secret for the OpenAI API key.

        Returns:
            A tuple containing (base_url, api_key_plain).
            base_url is None for OpenAI default.

        Raises:
            ValueError: If the provider is unsupported or the required key is missing.
        """
        base_url: Optional[str] = None
        api_key_secret: Optional[dagger.Secret] = None

        if provider == "openrouter":
            if not open_router_key:
                raise ValueError(
                    "open_router_api_key is required for provider 'openrouter'")
            base_url = "https://openrouter.ai/api/v1"
            api_key_secret = open_router_key
            print("Using OpenRouter provider.")
        elif provider == "openai":
            if not openai_key:
                raise ValueError(
                    "openai_api_key is required for provider 'openai'")
            base_url = None  # OpenAIProvider uses default if None
            api_key_secret = openai_key
            print("Using OpenAI provider.")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        # Retrieve plaintext key - this will implicitly check if the secret was assigned
        if not api_key_secret:
            # Should be caught by provider checks, but defensive programming
            raise ValueError(
                f"API key secret not found for provider '{provider}'.")

        return LLMCredentials(base_url=base_url, api_key=api_key_secret)
