import logging
from typing import Annotated, Dict, Optional, AsyncGenerator

import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig
from dagger import dag, function, object_type
from pydantic_ai import Agent, UnexpectedModelBehavior, RunContext
from typing_extensions import Doc
from user_intent.core.intent import (UserIntentAgentDependencies,
                                     create_user_intent_agent)
from user_intent.utils import create_llm_model, get_llm_credentials
from user_intent.models import GraphIntent, UserIntentState

# Add AG-UI imports
from pydantic_ai.ag_ui import (
    SSE_CONTENT_TYPE,
    StateDeps,
    handle_ag_ui_request
)
from starlette.requests import Request
from starlette.responses import Response


@object_type
class intent:
    """A class to encapsulate user intent agent functionality."""
    kind_of_graph: str
    graph_description: str


@object_type
class UserIntent:
    config: dict

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to YAML config file")]) -> 'UserIntent':
        """Create a UserIntentAgent instance with the given configuration."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict)

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "UserIntentAgent logging initialized. Configuration: %s", self.config)

    @function
    async def get_user_intent(
        self,
        provider: str,
        open_router_api_key: dagger.Secret,
        initial_prompt: Optional[str] = None,
        openai_api_key: Optional[dagger.Secret] = None,
    ) -> intent:
        """
        Run the user intent agent to help define a knowledge graph use case.

        Args:
            provider: LLM provider to use ('openai' or 'openrouter')
            open_router_api_key: API key for OpenRouter
            initial_prompt: Optional initial prompt from the user
            openai_api_key: API key for OpenAI

        Returns:
            An intent object containing the approved user goal
        """
        try:
            self.config = YAMLConfig(**self.config)
            self._setup_logging()

            # Get LLM credentials
            llm_credentials = await get_llm_credentials(
                provider=provider,
                open_router_key=open_router_api_key,
                openai_key=openai_api_key
            )

            # Create LLM model
            model = await create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name=self.config.core_api.model
            )

            # Create agent
            agent: Agent = create_user_intent_agent(pydantic_ai_model=model)
            agent.instrument_all()

            # Create dependencies with empty state
            deps = UserIntentAgentDependencies()

            # Run the agent with initial prompt if provided
            prompt = initial_prompt if initial_prompt else "I need help defining a knowledge graph use case."
            result = await agent.run(prompt, deps=deps)

            # Check if approved_user_goal was set
            if "approved_user_goal" not in deps.state:
                self.logger.warning(
                    "No approved user goal found in state after agent run.")
                return intent(
                    kind_of_graph="error",
                    graph_description="No approved user goal was set during the conversation."
                )

            # Convert the dictionary to an intent object
            approved_goal = deps.state["approved_user_goal"]
            return intent(
                kind_of_graph=approved_goal["kind_of_graph"],
                graph_description=approved_goal["graph_description"]
            )

        except UnexpectedModelBehavior as agent_error:
            self.logger.error(f"Error in UserIntentAgent: {agent_error}")
            return intent(
                kind_of_graph="error",
                graph_description=f"Agent error: {str(agent_error)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error in UserIntentAgent: {e}")
            return intent(
                kind_of_graph="error",
                graph_description=f"Unexpected error: {str(e)}"
            )

    @function
    async def create_ag_ui_app(
        self,
        provider: str,
        open_router_api_key: dagger.Secret,
        openai_api_key: Optional[dagger.Secret] = None,
    ) -> str:
        """
        Create an ASGI application for the UserIntentAgent using AG-UI protocol.

        Args:
            provider: LLM provider to use ('openai' or 'openrouter')
            open_router_api_key: API key for OpenRouter
            openai_api_key: API key for OpenAI

        Returns:
            A string confirming the app was created successfully and instructions
        """
        try:
            self.config = YAMLConfig(**self.config)
            self._setup_logging()

            # Get LLM credentials
            llm_credentials = await get_llm_credentials(
                provider=provider,
                open_router_key=open_router_api_key,
                openai_key=openai_api_key
            )

            # Create LLM model
            model = await create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name=self.config.core_api.model
            )

            # Create agent with AG-UI state support
            agent: Agent = create_user_intent_agent_with_ag_ui(
                pydantic_ai_model=model
            )

            # Return confirmation - actual app creation and serving would be done
            # in a separate setup since Dagger functions can't return ASGI apps
            return (
                "AG-UI app configured successfully. To serve this agent:\n"
                "1. Use the create_fastapi_app() function in user_intent/api.py\n"
                "2. Run with 'uvicorn user_intent.api:create_app(model_name, provider) --host 0.0.0.0 --port 8000'\n"
                "3. Connect your frontend to http://localhost:8000/agent"
            )

        except Exception as e:
            self.logger.error(f"Error creating AG-UI app: {e}")
            return f"Failed to create AG-UI app: {str(e)}"
