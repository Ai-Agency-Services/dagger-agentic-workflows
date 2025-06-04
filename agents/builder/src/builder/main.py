from typing import Annotated, Optional

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

    def _setup_logging(self):
        """Initializes logging for the Builder."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "Builder logging initialized. Configuration: %s", self.config)

    async def _install_dependencies(
        self,
        container: dagger.Container,
        llm_credentials: LLMCredentials
    ) -> dagger.Container:
        """Installs dependencies using OS detection first, then agent as fallback."""
        try:
            # First try using direct OS detection
            print("Installing dependencies using OS detection...")
            container_with_deps = await self._install_dependencies_by_os_detection(container)
            print(green("Dependencies installed successfully using OS detection."))
            return container_with_deps

        except Exception as e_detect:
            print(yellow(
                f"OS detection approach failed ({e_detect}), trying builder agent fallback..."))

            # Fall back to using the builder agent
            return await self._install_dependencies_with_agent(container, llm_credentials)

    async def _install_dependencies_by_os_detection(self, container: dagger.Container) -> dagger.Container:
        """Install dependencies based on OS detection."""
        try:
            print("Starting OS detection...")

            # Method 1: Check /etc/os-release first (most reliable)
            try:
                os_release = await container.with_exec(["sh", "-c", "cat /etc/os-release 2>/dev/null || echo 'not found'"]).stdout()

                if "ubuntu" in os_release.lower() or "debian" in os_release.lower():
                    print(green("Detected Debian/Ubuntu system via /etc/os-release"))
                    return await self._install_debian_deps(container)
                elif "alpine" in os_release.lower():
                    print(green("Detected Alpine system via /etc/os-release"))
                    return await self._install_alpine_deps(container)
            except Exception as e_os:
                print(
                    yellow(f"OS detection via /etc/os-release failed: {e_os}"))

            # Method 2: Check for package managers directly (with verification)
            package_managers = [
                # Try Debian/Ubuntu first since it's more common
                ("apt-get", "debian"),
                ("apk", "alpine"),
                ("yum", "rhel"),
                ("dnf", "fedora"),
                ("pacman", "arch")
            ]

            for pm, os_type in package_managers:
                try:
                    # First check if the package manager exists
                    pm_check = await container.with_exec(["sh", "-c", f"which {pm} || echo 'not found'"]).stdout()

                    # Important: Only consider it found if "not found" is NOT in the output
                    if "not found" not in pm_check:
                        print(
                            green(f"Detected {os_type} system with {pm} package manager"))

                        # Double verification step
                        if pm == "apk":
                            # Verify APK works before proceeding
                            verify = await container.with_exec(["sh", "-c", "apk --version || echo 'failed'"]).stdout()
                            if "failed" in verify:
                                print(
                                    yellow("False positive on apk detection, continuing search..."))
                                continue
                            return await self._install_alpine_deps(container)
                        elif pm == "apt-get":
                            # Verify apt-get works before proceeding
                            verify = await container.with_exec(["sh", "-c", "apt-get --version || echo 'failed'"]).stdout()
                            if "failed" in verify:
                                print(
                                    yellow("False positive on apt-get detection, continuing search..."))
                                continue
                            return await self._install_debian_deps(container)
                        else:
                            print(
                                yellow(f"Detected {os_type} but using generic approach"))
                            return await self._install_generic_deps(container)
                except Exception:
                    continue

            # Method 3: Try file-based detection as a last resort
            try:
                # Check for specific files that indicate OS type
                debian_check = await container.with_exec(["sh", "-c", "[ -f /etc/debian_version ] && echo 'debian' || echo 'not found'"]).stdout()
                if "debian" in debian_check:
                    print(green("Detected Debian-based system via /etc/debian_version"))
                    return await self._install_debian_deps(container)
            except Exception:
                pass

            # If we get here, try a generic approach
            print(yellow("Could not reliably detect OS, trying generic installation..."))
            return await self._install_generic_deps(container)

        except Exception as e:
            print(red(f"OS detection-based installation failed: {e}"))
            raise

    async def _install_dependencies_with_agent(
        self,
        container: dagger.Container,
        llm_credentials: LLMCredentials
    ) -> dagger.Container:
        """Install dependencies using the builder agent."""
        try:
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
                prompt="Install necessary dependencies including git, bash, tree, and github-cli.",
                deps=deps,
            )

            print(green("Agent dependencies installed using builder agent."))
            return deps.container
        except Exception as e_agent:
            print(red(f"Builder agent installation failed: {e_agent}"))
            raise

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

    async def _install_generic_deps(self, container: dagger.Container) -> dagger.Container:
        """Install dependencies using a generic approach when OS cannot be identified."""
        try:
            print(yellow("Using generic approach to install dependencies..."))

            # Try multiple commands with fallbacks
            try:
                # Try to install git using whatever package manager is available
                container = container.with_exec([
                    "sh", "-c",
                    "(apt-get update && apt-get install -y git bash tree curl) || " +
                    "(apk update && apk add --no-cache git bash tree curl) || " +
                    "(yum install -y git bash tree curl) || " +
                    "(dnf install -y git bash tree curl) || " +
                    "echo 'Failed to install using known package managers'"
                ])

                # Try to install GitHub CLI
                container = container.with_exec([
                    "sh", "-c",
                    "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null || true && " +
                    "curl -fsSL https://github.com/cli/cli/releases/download/v2.35.0/gh_2.35.0_linux_amd64.tar.gz -o /tmp/gh.tar.gz && " +
                    "mkdir -p /tmp/gh && tar -xzf /tmp/gh.tar.gz -C /tmp/gh --strip-components=1 && " +
                    "cp /tmp/gh/bin/gh /usr/local/bin/ 2>/dev/null || true"
                ])
            except Exception as e_install:
                print(
                    yellow(f"Generic installation partially failed: {e_install}"))

            # Basic verification
            try:
                git_version = await container.with_exec(["sh", "-c", "git --version || echo 'git not found'"]).stdout()
                if "git not found" not in git_version:
                    print(green(f"Git detected: {git_version.strip()}"))
            except Exception:
                pass

            print(yellow("Generic dependency installation completed with best effort"))
            return container
        except Exception as e:
            print(red(f"Generic dependency installation failed: {e}"))
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
        open_router_api_key: dagger.Secret,
        provider: str,
        openai_api_key: Optional[dagger.Secret] = None
    ) -> dagger.Container:
        """
        Builds the primary container environment for testing.
        """
        # Use one consistent path - config.container.work_dir
        self.config = YAMLConfig(**self.config)
        self._setup_logging()
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

            # Fixed the missing method call
            container_with_deps = await self._install_dependencies(self.base_container, llm_credentials)
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
        self._setup_logging()
        container = (
            base_container
            .with_secret_variable("GITHUB_TOKEN", token)
            .with_exec(["gh", "auth", "setup-git"])
            .with_exec(["gh", "auth", "status"])
            .with_exec(["git", "add", "."])
        )
        print(green("Pull request container setup complete."))
        return container
