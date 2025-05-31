from typing import Annotated

import dagger
import yaml
from ais_dagger_agents_config import YAMLConfig
from builder.core.builder_agent import (BuilderAgentDependencies,
                                        create_builder_agent)
from builder.models.llm_credentials import LLMCredentials
from builder.utils import create_llm_model, get_llm_credentials
from dagger import dag, function, object_type
from pydantic_ai import Agent
from simple_chalk import green, red, yellow
from typing_extensions import Doc


@object_type
class Builder:
    """Handles the setup of Dagger containers, prioritizing user's Dockerfile."""
    base_container: dagger.Container
    config: dict

    @classmethod
    async def create(cls, config_file: Annotated[dagger.File, Doc("Path to the YAML config file")]):
        """ Create a Clean object from a YAML config file """
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, base_container=dag.container())

    async def _install_agent_dependencies(
        self,
        container: dagger.Container,
        llm_credentials: LLMCredentials
    ) -> dagger.Container:
        """Installs agent-specific dependencies with robust OS detection."""
        try:
            # First try using the builder agent
            deps = BuilderAgentDependencies(container=container)
            print("Installing agent dependencies using builder agent...")

            model = await create_llm_model(
                api_key=llm_credentials.api_key,
                base_url=llm_credentials.base_url,
                model_name=self.config.core_api.model
            )

            builder_agent: Agent = create_builder_agent(
                pydantic_ai_model=model,
            )
            builder_agent.instrument_all()

            await builder_agent.run(
                prompt="Install necessary dependencies including git, bash, and github-cli.",
                deps=deps,
            )

            print(green("Agent dependencies installed using builder agent."))
            return deps.container
        except Exception as e_agent:
            print(yellow(
                f"Builder agent approach failed ({e_agent}), trying fallback detection..."))

            # More robust fallback approach
            return await self._install_dependencies_fallback(container)

    async def _install_dependencies_fallback(self, container: dagger.Container) -> dagger.Container:
        """Fallback dependency installation with better OS detection."""
        try:
            # Try to identify the base image more reliably
            # Method 1: Check for package managers directly
            package_managers = [
                ("apk", "alpine"),
                ("apt-get", "debian"),
                ("yum", "rhel"),
                ("dnf", "fedora"),
                ("pacman", "arch")
            ]

            detected_pm = None
            for pm, os_type in package_managers:
                try:
                    # Use 'which' or 'command -v' to check for package manager
                    result = await container.with_exec(["sh", "-c", f"command -v {pm} >/dev/null 2>&1 && echo 'found' || echo 'not_found'"]).stdout()
                    if "found" in result.strip():
                        detected_pm = (pm, os_type)
                        print(
                            f"Detected {os_type} system with {pm} package manager")
                        break
                except Exception:
                    continue

            if detected_pm:
                pm, os_type = detected_pm
                if os_type == "alpine":
                    return await self._install_alpine_deps(container)
                elif os_type in ["debian", "ubuntu"]:
                    return await self._install_debian_deps(container)
                else:
                    print(
                        yellow(f"Detected {os_type} but using generic approach"))
                    return await self._install_generic_deps(container)

            # Method 2: Try to detect by running simple commands
            try:
                # Test basic shell functionality first
                test_result = await container.with_exec(["sh", "-c", "echo 'shell_works'"]).stdout()
                if "shell_works" not in test_result:
                    raise RuntimeError("Basic shell not working")

                # Try to identify OS by checking common files/commands
                os_checks = [
                    ("cat /etc/os-release 2>/dev/null | head -1", "os-release"),
                    ("cat /etc/alpine-release 2>/dev/null", "alpine"),
                    ("cat /etc/debian_version 2>/dev/null", "debian"),
                    ("uname -a 2>/dev/null", "uname")
                ]

                for cmd, check_type in os_checks:
                    try:
                        result = await container.with_exec(["sh", "-c", cmd]).stdout()
                        if result.strip():
                            print(
                                f"OS info from {check_type}: {result.strip()[:100]}")

                            if "alpine" in result.lower():
                                return await self._install_alpine_deps(container)
                            elif any(term in result.lower() for term in ["debian", "ubuntu"]):
                                return await self._install_debian_deps(container)
                            break
                    except Exception:
                        continue

                # If we get here, try a generic approach
                print(
                    yellow("Could not detect specific OS, trying generic installation..."))
                return await self._install_generic_deps(container)

            except Exception as e_shell:
                print(red(f"Shell functionality test failed: {e_shell}"))
                # Last resort - return container as-is with warning
                print(yellow("Returning container without additional dependencies"))
                return container

        except Exception as e:
            print(red(f"Fallback dependency installation failed: {e}"))
            return container

    async def _install_alpine_deps(self, container: dagger.Container) -> dagger.Container:
        """Install dependencies using Alpine package manager."""
        try:
            # First verify we can run the apk command
            test_container = await container.with_exec(["sh", "-c", "which apk || echo 'apk not found'"]).stdout()
            if "not found" in test_container:
                raise RuntimeError(
                    "apk command not available in this container")

            print("Installing dependencies with apk...")
            container = container.with_exec(["apk", "update"])
            container = container.with_exec(
                ["apk", "add", "--no-cache", "git", "bash", "tree"])

            # GitHub CLI might need to be installed differently on Alpine
            try:
                container = container.with_exec([
                    "sh", "-c",
                    "apk add --no-cache github-cli || " +
                    "(apk add curl && " +
                    "wget -O /tmp/gh.tar.gz https://github.com/cli/cli/releases/download/v2.35.0/gh_2.35.0_linux_amd64.tar.gz && " +
                    "tar -xzf /tmp/gh.tar.gz -C /tmp && " +
                    "mv /tmp/gh*/bin/gh /usr/local/bin/)"
                ])
            except Exception as e_gh:
                print(
                    yellow(f"Could not install GitHub CLI: {e_gh}, continuing anyway..."))

            print(green("Successfully installed dependencies with apk"))
            return container
        except Exception as e:
            print(red(f"Failed to install dependencies with apk: {e}"))
            raise

    async def _install_debian_deps(self, container: dagger.Container) -> dagger.Container:
        """Install dependencies using Debian/Ubuntu package manager."""
        try:
            print("Installing dependencies with apt-get...")
            container = container.with_exec(["apt-get", "update"])
            container = container.with_exec(
                ["apt-get", "install", "-y", "git", "bash", "tree", "curl", "wget"])

            # Install GitHub CLI on Debian
            try:
                container = container.with_exec([
                    "sh", "-c",
                    "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && " +
                    "chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && " +
                    "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] " +
                    "https://cli.github.com/packages stable main\" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && " +
                    "apt-get update && apt-get install -y gh"
                ])
            except Exception as e_gh:
                print(
                    yellow(f"Could not install GitHub CLI: {e_gh}, continuing anyway..."))

            print(green("Successfully installed dependencies with apt-get"))
            return container
        except Exception as e:
            print(red(f"Failed to install dependencies with apt-get: {e}"))
            raise

    def _configure_git(self, container: dagger.Container) -> dagger.Container:
        """Configures git user name and email in the container."""
        print("Configuring git user...")
        return (
            container
            .with_exec(["git", "config", "--global", "user.email", self.config.git.user_email])
            .with_exec(["git", "config", "--global", "user.name", self.config.git.user_name])
            .with_exec(["git", "config", "--global", "safe.directory", self.config.container.work_dir])
        )

    @function
    async def build_test_environment(
        self,
        source: dagger.Directory,
        dockerfile_path: str,
        openai_api_key: dagger.Secret,
        open_router_api_key: dagger.Secret,
        provider: str
    ) -> dagger.Container:
        """
        Builds the primary container environment for testing.
        """
        # Use one consistent path - config.container.work_dir
        self.config = YAMLConfig(**self.config)
        work_dir = self.config.container.work_dir

        if dockerfile_path:
            try:
                print(
                    f"Attempting to build container from Dockerfile: {dockerfile_path}")

                # First check if the Dockerfile exists
                dockerfile_exists = await source.file(dockerfile_path).id()
                if not dockerfile_exists:
                    raise ValueError(
                        f"Dockerfile not found at path: {dockerfile_path}")

                self.base_container = (
                    dag.container()
                    .build(
                        context=source,
                        dockerfile=dockerfile_path
                    )
                    # Mount source at the specified work_dir
                    .with_directory(work_dir, source)
                    .with_workdir(work_dir)
                )
                print(
                    green(f"Successfully built base container from Dockerfile: {dockerfile_path}"))
            except Exception as e:
                print(
                    red(f"Failed to build from Dockerfile '{dockerfile_path}': {e}"))
                print(yellow("Falling back to default Alpine image."))
                self.base_container = (
                    dag.container()
                    .from_("alpine:latest")
                    .with_directory(work_dir, source)
                    .with_workdir(work_dir)
                )
        else:
            print(yellow("No Dockerfile path provided. Using default Alpine image."))
            self.base_container = (
                dag.container()
                .from_("alpine:latest")
                .with_directory(work_dir, source)
                .with_workdir(work_dir)
            )

        # More robust dependency installation
        try:
            llm_credentials = await get_llm_credentials(
                openai_key=openai_api_key,
                open_router_key=open_router_api_key,
                provider=provider
            )

            container_with_deps = await self._install_agent_dependencies(self.base_container, llm_credentials)
            git_container = self._configure_git(container_with_deps)

            # Run the reporter command with error handling
            if self.config.reporter:
                cmd = f'cd {work_dir} && {self.config.reporter.command} || echo "Reporter command failed with exit code $?"'
                final_container = git_container.with_exec(["bash", "-c", cmd])
            else:
                print(yellow("No reporter command specified, skipping execution."))
                final_container = git_container

            print(green("Test environment container setup complete."))
            return final_container
        except Exception as e:
            print(red(f"Failed to set up test environment: {e}"))
            # Return the base container if we at least got that far
            print(yellow("Returning base container without full setup"))
            return self.base_container

    @function
    def setup_pull_request_container(
        self, base_container: dagger.Container, token: dagger.Secret
    ) -> dagger.Container:
        """
        Sets up the container for managing pull requests, starting from a base container.

        Args:
            base_container: The container already built with user and agent dependencies.
            token: The GitHub token secret.

        Returns:
            A container configured for PR operations.
        """
        print("Configuring container for pull requests...")
        container = (
            base_container
            .with_secret_variable("GITHUB_TOKEN", token)
            .with_exec(["gh", "auth", "setup-git"])
            .with_exec(["gh", "auth", "status"])
            .with_exec(["git", "add", "."])
        )
        print(green("Pull request container setup complete."))
        return container
