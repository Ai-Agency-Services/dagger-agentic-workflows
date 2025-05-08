import dagger
from coverage_agent.models.config import YAMLConfig
from dagger import dag
from simple_chalk import green, red, yellow


class ContainerBuilder:
    """Handles the setup of Dagger containers, prioritizing user's Dockerfile."""

    def __init__(self, config: YAMLConfig):
        self.config = config

    # TODO: """ use and agent for this """
    def _install_agent_dependencies(self, container: dagger.Container) -> dagger.Container:
        """Installs agent-specific dependencies (git, bash, gh) into an existing container."""
        try:
            # Try debian first
            print("Attempting to install agent dependencies using apt...")
            container = (
                container
                # Avoid prompts
                .with_env_variable("DEBIAN_FRONTEND", "noninteractive")
                .with_exec(["apt-get", "update", "-y"])
                .with_exec(["apt-get", "install", "-y", "--no-install-recommends", "git", "bash", "gh", "tree"])
                .with_exec(["apt-get", "clean"])  # Clean up cache
            )
            print(green("Agent dependencies installed using apt."))
            return container
        except Exception as e_apk:
            print(yellow(f"apk failed ({e_apk}), trying apt..."))
            try:
                # Try apk alpine as a fallback
                print("Attempting to install agent dependencies using apk...")
                container = (
                    container
                    .with_exec(["apk", "update"])
                    .with_exec(["apk", "add", "--no-cache", "git", "bash", "github-cli",  "tree"])
                )
                print(green("Agent dependencies installed using apk."))
                return container
            except Exception as e_apt:
                print(
                    red(f"Failed to install agent dependencies using apk or apt: {e_apt}"))
                raise RuntimeError(
                    "Could not install agent dependencies (git, bash, gh) into the base container.") from e_apt

    def _configure_git(self, container: dagger.Container) -> dagger.Container:
        """Configures git user name and email in the container."""
        print("Configuring git user...")
        return (
            container
            .with_exec(["git", "config", "--global", "user.email", self.config.git.user_email])
            .with_exec(["git", "config", "--global", "user.name", self.config.git.user_name])
        )

    def build_test_environment(
        self,
        source: dagger.Directory,
        config: YAMLConfig,
        dockerfile_path: str = None,
    ) -> dagger.Container:
        """
        Builds the primary container environment for testing.

        Prioritizes building from the user's Dockerfile if provided,
        then installs agent dependencies. Falls back to Alpine if no
        Dockerfile is specified.

        Args:
            source: The user's source code directory.
            dockerfile_path: Relative path to the user's Dockerfile within the source directory.

        Returns:
            A configured Dagger container.
        """
        base_container: dagger.Container

        if dockerfile_path:
            # Ensure dockerfile exists in source
            # Assuming source is mounted at /workspace
            try:
                print(
                    f"Attempting to build container from Dockerfile: {dockerfile_path}")
                base_container = dag.container().with_workdir(config.container.work_dir).build(
                    context=source,
                    dockerfile=dockerfile_path  # Path relative to context
                )
                print(
                    green(f"Successfully built base container from Dockerfile: {dockerfile_path}"))
            except Exception as e:
                print(
                    red(f"Failed to build from Dockerfile '{dockerfile_path}': {e}"))
                print(yellow("Falling back to default Alpine image."))
                base_container = dag.container().from_("alpine:latest")
                base_container = base_container.with_directory(
                    "/workspace", source)

        else:
            print(yellow("No Dockerfile path provided. Using default Alpine image."))
            base_container = dag.container().from_("alpine:latest")
            base_container = base_container.with_directory(
                "/workspace", source)

        container_with_deps = self._install_agent_dependencies(base_container)

        git_container = self._configure_git(container_with_deps)
        final_container = git_container.with_exec(
            [
                "bash",
                "-c",
                f"{self.config.reporter.command}" +
                "; echo -n $? > /exit_code",
            ]
        )

        print(green("Test environment container setup complete."))
        return final_container

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
        )
        print(green("Pull request container setup complete."))
        return container
