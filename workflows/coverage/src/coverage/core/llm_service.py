import os
import traceback
import json
from abc import ABC, abstractmethod
from typing import List, Optional

from coverage.models.code_module import CodeModule
from openai import OpenAI
from simple_chalk import red


class BaseLLMService(ABC):
    """Base class for OpenAI-compatible LLM services."""

    def __init__(self, openai_client: OpenAI = None):
        self.openai_client = openai_client or self._create_openai_client()

    @abstractmethod
    def _get_base_url(self) -> str:
        """Returns the base URL for the specific provider."""
        pass

    @abstractmethod
    def _get_api_key_env_var(self) -> str:
        """Returns the environment variable name for the API key."""
        pass

    def _create_openai_client(self) -> OpenAI:
        api_key = os.getenv(self._get_api_key_env_var())
        if not api_key:
            raise ValueError(
                f"API key environment variable '{self._get_api_key_env_var()}' not set.")
        return OpenAI(
            base_url=self._get_base_url(),
            api_key=api_key,
        )

    def generate_code_module(
        self,
        model: str,
        system_prompt: str,
        user_messages: list = None,
        fallback_models: Optional[List[str]] = None
    ) -> CodeModule:
        try:
            messages = [{"role": "system", "content": system_prompt}]
            if user_messages:
                if isinstance(user_messages, str):
                    messages.append({"role": "user", "content": user_messages})
                elif isinstance(user_messages, list):
                    for msg in user_messages:
                        if isinstance(msg, str):
                            messages.append({"role": "user", "content": msg})
                        elif isinstance(msg, dict) and "role" in msg and "content" in msg:
                            messages.append(msg)

            # Use a type checking approach that doesn't require importing OpenRouterService
            extra_body = None
            # Check the base URL instead of using isinstance
            if self._get_base_url() == "https://api.openrouter.ai/v1" and fallback_models:
                extra_body = {"models": fallback_models}

            chat_completion = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"} if CodeModule.model_json_schema()[
                    'type'] == 'json_object' else None,
                extra_body=extra_body
            )

            result_content = chat_completion.choices[0].message.content
            try:
                module_data = json.loads(result_content)
                return CodeModule(**module_data)
            except Exception as parse_error:
                print(
                    red(f"Failed to parse response into CodeModule: {parse_error}"))
                print(red(f"Raw response content: {result_content}"))
                raise Exception("Failed to generate or parse code module.")

        except Exception as e:
            print(red(f"Error generating code module: {e}"))
            print(traceback.format_exc())
            raise e


# Provider implementations
class OpenRouterService(BaseLLMService):
    """OpenRouter implementation of BaseLLMService."""

    def _get_base_url(self) -> str:
        return "https://api.openrouter.ai/v1"

    def _get_api_key_env_var(self) -> str:
        return "OPEN_ROUTER_API_KEY"


class OpenAIService(BaseLLMService):
    """OpenAI implementation of BaseLLMService."""

    def _get_base_url(self) -> str:
        return "https://api.openai.com/v1"

    def _get_api_key_env_var(self) -> str:
        return "OPENAI_API_KEY"
