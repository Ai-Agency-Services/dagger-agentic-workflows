from typing import NamedTuple, Optional

import dagger
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from simple_chalk import red


class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: dagger.Secret


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
        print(f"🔧 DEBUG: Using OpenRouter provider with base_url: {base_url}")
    elif provider == "openai":
        if not openai_key:
            raise ValueError(
                "openai_api_key is required for provider 'openai'")
        base_url = None  # OpenAIProvider uses default if None
        api_key_secret = openai_key
        print(f"🔧 DEBUG: Using OpenAI provider with base_url: {base_url or 'https://api.openai.com/v1 (default)'}")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    # Retrieve plaintext key - this will implicitly check if the secret was assigned
    if not api_key_secret:
        # Should be caught by provider checks, but defensive programming
        raise ValueError(
            f"API key secret not found for provider '{provider}'.")

    return LLMCredentials(base_url=base_url, api_key=api_key_secret)


async def create_llm_model(
    api_key: dagger.Secret,
    base_url: Optional[str],
    model_name: str
) -> OpenAIModel:
    """
    Creates the Pydantic AI model instance (currently OpenAIModel).

    Args:
        api_key: The API key as Dagger secret.
        base_url: The base URL for the API (None for OpenAI default).
        model_name: The specific model name to use.

    Returns:
        An instance of OpenAIModel.

    Raises:
        Exception: If initialization of the provider or model fails.
    """
    try:
        print(f"🔧 DEBUG: Creating LLM model with:")
        print(f"🔧 DEBUG: - model_name: {model_name}")
        print(f"🔧 DEBUG: - base_url: {base_url}")
        
        api_key_plain = await api_key.plaintext()
        print(f"🔧 DEBUG: - api_key length: {len(api_key_plain) if api_key_plain else 0}")
        
        llm_provider = OpenAIProvider(api_key=api_key_plain, base_url=base_url)
        # Determine effective base URL for logging
        effective_base_url = base_url if base_url else "https://api.openai.com/v1"
        pydantic_ai_model = OpenAIModel(
            model_name=model_name, provider=llm_provider)
        print(
            f"🔧 DEBUG: Pydantic AI Model created for '{model_name}' using effective base URL: {effective_base_url}")
        return pydantic_ai_model
    except Exception as e:
        print(red(f"🔧 DEBUG: Failed to initialize Pydantic AI Provider/Model: {e}"))
        raise
