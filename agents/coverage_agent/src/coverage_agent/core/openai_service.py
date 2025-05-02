from coverage_agent.core.llm_service import BaseLLMService


class OpenAIService(BaseLLMService):
    def _get_base_url(self) -> str:
        # OpenAI uses a default base URL if not specified, or you can set it explicitly
        return "https://api.openai.com/v1"

    def _get_api_key_env_var(self) -> str:
        return "OPENAI_API_KEY"
