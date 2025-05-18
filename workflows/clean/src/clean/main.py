import asyncio
from typing import Annotated, NamedTuple, Optional

import dagger
import yaml
from clean.core.clean_names_workflow import clean_names_workflow
from clean.models.config import YAMLConfig
from dagger import Doc, function, object_type
from simple_chalk import red


class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: str


@object_type
class Clean:
    config: dict
    llm_credentials: LLMCredentials

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to the YAML config file")]) -> "Clean":
        """ Create a Clean object from a YAML config file """
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, llm_credentials=None)

    @function
    async def meaningful_names(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        supabase_url: Annotated[str, Doc("Supabase project URL")],
        supabase_key: Annotated[dagger.Secret, Doc("Supabase API key")],
        repository_url: Annotated[str, Doc("Repository URL to generate tests for")],
        branch: Annotated[str, Doc("Branch to generate tests for")],
    ) -> str:
        """ Refactor the code to use meaningful names """
        try:
            self.config: YAMLConfig = YAMLConfig(**self.config)
            asyncio.run(clean_names_workflow(
                config=self.config,
                provider=self.config.llm.provider,
                open_router_api_key=self.config.llm.open_router_api_key,
                openai_api_key=self.config.llm.openai_api_key,
                github_access_token=github_access_token,
                repo_url=repository_url,
                branch=branch,
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                model_name=self.config.llm.model_name,
                max_files=self.config.generation.max_files
            ))
        except Exception as e:
            print(red(f"Error during workflow execution: {e}"))
            raise

        return "Workflow completed successfully!"
