from coverage_agent.core.llm_service import BaseLLMService


class OpenRouterService(BaseLLMService):
    def _get_base_url(self) -> str:
        return "https://api.openrouter.ai/v1"

    def _get_api_key_env_var(self) -> str:
        return "OPEN_ROUTER_API_KEY"
