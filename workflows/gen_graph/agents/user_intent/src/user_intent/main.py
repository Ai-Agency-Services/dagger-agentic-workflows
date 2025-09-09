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

    @function
    async def get_user_intent_interactive(
        self,
        provider: str,
        open_router_api_key: dagger.Secret,
        initial_prompt: Optional[str] = None,
        openai_api_key: Optional[dagger.Secret] = None,
        interactive_inputs: Optional[list[str]] = None,
        non_interactive_fallback: bool = False
    ) -> intent:
        """
        Run the user intent agent in interactive CLI mode to define a knowledge graph use case.

        Args:
            provider: LLM provider to use ('openai' or 'openrouter')
            open_router_api_key: API key for OpenRouter
            initial_prompt: Optional initial prompt from the user
            openai_api_key: API key for OpenAI
            interactive_inputs: Optional list of inputs to feed to the conversation (for non-interactive environments)
            non_interactive_fallback: If True, use a default conversation flow when stdin is unavailable

        Returns:
            An intent object containing the approved user goal
        """
        # Set up logging first to avoid AttributeError
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)

        try:
            # Add missing git configuration to avoid validation errors
            config_dict = dict(self.config)
            if "git" not in config_dict:
                config_dict["git"] = {}
            if "base_pull_request_branch" not in config_dict.get("git", {}):
                config_dict["git"]["base_pull_request_branch"] = "main"
                logger.info("Added default git.base_pull_request_branch: main")

            # Log configuration before validation
            logger.info("UserIntentAgent initializing with configuration")

            try:
                # Validate config with Pydantic
                validated_config = YAMLConfig(**config_dict)
                self.config = validated_config
            except Exception as config_error:
                logger.error(f"Configuration validation error: {config_error}")
                return intent(
                    kind_of_graph="error",
                    graph_description=f"Configuration error: {str(config_error)}"
                )

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

            # Initialize conversation with prompt or default
            message = initial_prompt if initial_prompt else "I need help defining a knowledge graph use case."
            print(f"\n🧠 User: {message}")

            # Set up interactive inputs if provided
            input_iter = iter(interactive_inputs or [])

            # Track if we're in fallback mode due to stdin issues
            using_fallback = False

            # Interactive conversation loop
            while True:
                # Run agent with current message
                response = await agent.run(message, deps=deps)
                print(f"\n🤖 Agent: {response}\n")

                # Check if we have an approved user goal and can exit
                if "approved_user_goal" in deps.state:
                    print("\n✅ User goal approved. Conversation complete.")
                    break

                # Try to get the next input based on available sources
                try:
                    # If we have predefined inputs, use those first
                    if interactive_inputs:
                        try:
                            message = next(input_iter)
                            print(f"🧠 User: {message}")
                            continue
                        except StopIteration:
                            print("\n⚠️ No more pre-defined inputs.")
                            if not non_interactive_fallback:
                                break
                            using_fallback = True

                    # If we're in a non-interactive environment or hit EOF before
                    if using_fallback or non_interactive_fallback:
                        # Use a simple fallback conversation to generate a knowledge graph
                        if "product" in str(response).lower() or "supply" in str(response).lower():
                            message = "I want to create a supply chain knowledge graph for tracking product dependencies"
                            print(f"🧠 User (fallback): {message}")
                        else:
                            message = "Let's do a product dependency knowledge graph that shows relationships between components"
                            print(f"🧠 User (fallback): {message}")

                        # Only run through fallback conversation once
                        using_fallback = True
                        continue

                    # Otherwise try to get interactive input
                    print("\nEnter your response (or type 'exit' to end conversation):")
                    message = input("🧠 User: ")

                except (EOFError, KeyboardInterrupt):
                    print("\n⚠️ Input stream ended or interrupted.")

                    # If fallback is enabled, continue with default responses
                    if non_interactive_fallback and not using_fallback:
                        using_fallback = True
                        message = "I want to create a product dependency graph"
                        print(f"🧠 User (fallback): {message}")
                        continue
                    else:
                        print("Ending conversation.")
                        break

                # Check for exit commands
                if message.lower() in ["exit", "quit", "done", "bye"]:
                    print("\n👋 Ending conversation.")
                    break

            # If we're in fallback mode and still don't have an approved goal,
            # make one final attempt with a very specific request
            if using_fallback and "approved_user_goal" not in deps.state:
                logger.info("Using fallback to create a default approved goal")
                final_message = ("I want to create a product dependency knowledge graph "
                                 "to track relationships between components and suppliers")
                print(f"\n🧠 User (fallback): {final_message}")
                await agent.run(final_message, deps=deps)

            # Check if approved_user_goal was set
            if "approved_user_goal" not in deps.state:
                logger.warning(
                    "No approved user goal found in state after conversation.")
                # Create a default goal in non-interactive mode
                if non_interactive_fallback:
                    logger.info("Creating default knowledge graph goal")
                    return intent(
                        kind_of_graph="product dependency",
                        graph_description="A knowledge graph for tracking product dependencies between components and suppliers"
                    )
                else:
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
            logger.error(f"Error in UserIntentAgent: {agent_error}")
            return intent(
                kind_of_graph="error",
                graph_description=f"Agent error: {str(agent_error)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in UserIntentAgent: {e}")
            return intent(
                kind_of_graph="error",
                graph_description=f"Unexpected error: {str(e)}"
            )
