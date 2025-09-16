from typing import Optional
import dagger
from ais_dagger_agents_config import LLMCredentials
from pydantic_ai.models.openai import OpenAIModel

async def get_llm_credentials(config: dict, api_key: dagger.Secret, is_open_router: bool = False) -> LLMCredentials:
    base_url = None
    if is_open_router:
        base_url = "https://openrouter.ai/api/v1"
    elif "core_api" in config and config["core_api"].get("provider") == "openrouter":
        base_url = "https://openrouter.ai/api/v1"
    return LLMCredentials(base_url=base_url, api_key=api_key)

def create_llm_model(credentials: LLMCredentials, model_name: str) -> OpenAIModel:
    return OpenAIModel(model_name=model_name, api_key=credentials.api_key, base_url=credentials.base_url)
