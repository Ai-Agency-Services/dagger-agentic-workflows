import dagger
from dagger import dag, function, object_type


@object_type
class SpecKit:
    """
    A Dagger module for GitHub Spec Kit (specify-cli).

    Provides a generic wrapper around the specify command-line tool,
    avoiding the need to update this module when the CLI changes.
    """

    @function
    async def container(
        self,
        source: dagger.Directory | None = None,
    ) -> dagger.Container:
        """
        Returns a container with specify-cli installed and ready to use.

        Args:
            source: Optional source directory to mount at /work
        """
        ctr = (
            dag.container()
            .from_("ghcr.io/astral-sh/uv:debian")
            .with_workdir("/work")
            .with_exec(["uv", "venv", ".venv"])
            .with_exec([
                "bash", "-c",
                ". .venv/bin/activate && uv pip install git+https://github.com/github/spec-kit.git"
            ])
            .with_env_variable("VIRTUAL_ENV", "/work/.venv")
            .with_env_variable("PATH", "/work/.venv/bin:$PATH", expand=True)
        )

        if source is not None:
            ctr = ctr.with_directory("/work", source)

        return ctr

    @function
    async def exec(
        self,
        args: list[str],
        source: dagger.Directory | None = None,
        env: list[str] | None = None,
    ) -> dagger.Container:
        """
        Execute specify command with arbitrary arguments.

        Returns the container after execution for chaining or directory extraction.

        Args:
            args: Arguments to pass to specify (e.g., ["init", "--here", "--ai", "claude"])
            source: Optional source directory to mount at /work
            env: Optional environment variables in KEY=VALUE format

        Examples:
            dagger call exec --args init --args my-project --args --ai --args claude
            dagger call exec --args init --args --here --args --force --source .
            dagger call exec --args validate --args specs --source .
        """
        ctr = await self.container(source)

        # Apply environment variables if provided
        if env:
            for var in env:
                if "=" in var:
                    key, value = var.split("=", 1)
                    ctr = ctr.with_env_variable(key, value)

        return ctr.with_exec(["specify"] + args)

    @function
    async def run(
        self,
        args: list[str],
        source: dagger.Directory | None = None,
        env: list[str] | None = None,
    ) -> str:
        """
        Execute specify command and return stdout.

        Args:
            args: Arguments to pass to specify
            source: Optional source directory to mount at /work
            env: Optional environment variables in KEY=VALUE format

        Examples:
            dagger call run --args --help
            dagger call run --args init --args --help
        """
        ctr = await self.exec(args, source, env)
        return await ctr.stdout()

    @function
    async def directory(
        self,
        args: list[str],
        source: dagger.Directory | None = None,
        path: str = "/work",
        env: list[str] | None = None,
    ) -> dagger.Directory:
        """
        Execute specify command and return a directory.

        Useful for init/generate commands that modify files.

        Args:
            args: Arguments to pass to specify
            source: Optional source directory to mount at /work
            path: Path to extract from container (default: /work)
            env: Optional environment variables in KEY=VALUE format

        Examples:
            dagger call directory --args init --args my-project --path /work/my-project
            dagger call directory --args init --args --here --source . export --path .
        """
        ctr = await self.exec(args, source, env)
        return ctr.directory(path)
