import logging
from typing import Annotated, Optional

import dagger
import yaml
from ais_dagger_agents_config import LLMCredentials, YAMLConfig
from dagger import dag, function, object_type
from pull_request_agent.core.pull_request_agent import (
    PullRequestAgentDependencies, create_pull_request_agent)
from pull_request_agent.utils import create_llm_model, get_llm_credentials
from pydantic_ai import Agent, UnexpectedModelBehavior
from typing_extensions import Doc


@object_type
class PullRequestAgent:
    config: dict
    container: dagger.Container

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to YAML config file")]) -> 'PullRequestAgent':
        """ Create a PullRequestAgent instance with the given configuration and container. """
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, container=dag.container())

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "PullRequestAgent logging initialized. Configuration: %s", self.config)

    @function
    async def run(
        self,
        container: dagger.Container,
        provider: str,
        open_router_api_key: dagger.Secret,
        error_context: Optional[str] = None,
        insight_context: Optional[str] = None,
        openai_api_key: Optional[dagger.Secret] = None,
    ) -> dagger.Container:
        """ Run the pull request agent with the given dependencies."""

        async def _run_agent(
            self,
            llm_credentials: LLMCredentials,
            container: dagger.Container,
            error_context: Optional[str] = None,
            insight_context: Optional[str] = None,
        ) -> dagger.Container:
            try:
                self._setup_logging()
                deps = PullRequestAgentDependencies(
                    config=self.config,
                    container=container,
                    error_context=error_context,
                    insight_context=insight_context
                )
                model = await create_llm_model(
                    api_key=llm_credentials.api_key,
                    base_url=llm_credentials.base_url,
                    model_name=self.config.core_api.model
                )
                agent: Agent = create_pull_request_agent(
                    pydantic_ai_model=model)
                agent.instrument_all()
                result = await agent.run(
                    '''Create a pull request with the newly generated code.
                    Ensure the pull request includes a description of the changes made, any relevant context, related issues or discussions.''',
                    deps=deps
                )
                messages = result.all_messages()
                self.logger.info(
                    f"Agent completed with {len(messages)} messages")

                if result.usage:
                    print(f"Token usage: {result.usage()} tokens")

                return await deps.container.with_new_file("/status.txt", "success").sync()
            except UnexpectedModelBehavior as agent_error:
                self.logger.error(
                    f"Error creating PullRequestAgentDependencies: {agent_error}")
                print(f"Error running Pull Request Agent: {agent_error}")
                return await container.with_new_file("/error.txt", str(agent_error))

        try:
            self.config = YAMLConfig(**self.config)
            llm_credentials = await get_llm_credentials(
                provider=provider,
                open_router_key=open_router_api_key,
                openai_key=openai_api_key
            )
            return await _run_agent(
                self,
                llm_credentials=llm_credentials,
                container=container,
                error_context=error_context,
                insight_context=insight_context
            )

        except Exception as e:
            self.logger.error(f"Error creating PullRequestAgent: {e}")
            return await container.with_new_file("/error.txt", str(e))
