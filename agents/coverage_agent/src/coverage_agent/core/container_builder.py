import dagger
from coverage_agent.core.builder_agent import (BuilderAgentDependencies,
                                               create_builder_agent)
from coverage_agent.models.config import YAMLConfig
from dagger import dag
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from simple_chalk import green, red, yellow
from typing import Optional


class ContainerBuilder:
    """Handles the setup of Dagger containers, prioritizing user's Dockerfile."""
    base_container: dagger.Container
    builder_agent: Agent

    def __init__(self, config: YAMLConfig, model: OpenAIModel):
        self.config = config
        self.model = model

    async def _install_agent_dependencies(self, container: dagger.Container) -> dagger.Container:
        """Installs agent-specific dependencies (git, bash, gh) into an existing container."""
        try:
            # First try using the builder agent
            deps = BuilderAgentDependencies(container=container)
            print("Installing agent dependencies using builder agent...")
            self.builder_agent = create_builder_agent(
                pydantic_ai_model=self.model)
            self.builder_agent.instrument_all()

            await self.builder_agent.run(
                prompt="Install necessary dependencies including git, bash, and github-cli.",
                deps=deps,
            )

            print(green("Agent dependencies installed using builder agent."))
            return deps.container
        except Exception as e_agent:
            print(yellow(
                f"Builder agent approach failed ({e_agent}), trying to detect OS..."))

            # Check OS type first
            try:
                # Use file existence to determine OS type
                alpine_check = await container.with_exec(["test", "-f", "/etc/alpine-release"]).exit_code()
                debian_check = await container.with_exec(["test", "-f", "/etc/debian_version"]).exit_code()

                if alpine_check == 0:
                    print("Detected Alpine Linux, using apk...")
                    return await self._install_alpine_deps(container)
                elif debian_check == 0:
                    print("Detected Debian/Ubuntu, using apt...")
                    return await self._install_debian_deps(container)
                else:
                    # Try to determine by command availability
                    which_apk = await container.with_exec(["which", "apk"]).exit_code()
                    if which_apk == 0:
                        print("Found apk, using Alpine package manager...")
                        return await self._install_alpine_deps(container)

                    which_apt = await container.with_exec(["which", "apt-get"]).exit_code()
                    if which_apt == 0:
                        print("Found apt-get, using Debian package manager...")
                        return await self._install_debian_deps(container)

                    # Last resort - try sh to see if we can at least run basic commands
                    print(
                        yellow("Could not determine OS type, trying basic shell commands..."))
                    container = container.with_exec(
                        ["sh", "-c", "echo 'Checking basic shell functionality'"])
                    raise RuntimeError(
                        "Could not determine OS package manager")

            except Exception as e_os:
                print(
                    red(f"Failed to detect OS or run basic commands: {e_os}"))
                raise RuntimeError(
                    "Container appears to be missing basic shell functionality") from e_os

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

    async def build_test_environment(
        self,
        source: dagger.Directory,
        config: YAMLConfig,
        dockerfile_path: str = None,
    ) -> dagger.Container:
        """
        Builds the primary container environment for testing.
        """
        # Use one consistent path - config.container.work_dir
        work_dir = config.container.work_dir

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
            container_with_deps = await self._install_agent_dependencies(self.base_container)
            git_container = self._configure_git(container_with_deps)

            # Run the reporter command with error handling
            cmd = f'cd {work_dir} && {self.config.reporter.command} || echo "Reporter command failed with exit code $?"'
            final_container = git_container.with_exec(["bash", "-c", cmd])

            print(green("Test environment container setup complete."))
            return final_container
        except Exception as e:
            print(red(f"Failed to set up test environment: {e}"))
            # Return the base container if we at least got that far
            print(yellow("Returning base container without full setup"))
            return self.base_container

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
