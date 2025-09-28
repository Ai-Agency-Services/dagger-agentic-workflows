"""Test Environment Configurator agent."""

from dataclasses import dataclass
from typing import Optional
import json
import dagger
from ais_dagger_agents_config import YAMLConfig
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from simple_chalk import blue, green, yellow
from ..utils.container_state import write_json, append_log
from .models import TestEnvConfig


@dataclass
class TestEnvDependencies:
    """Dependencies for TestEnv agent."""
    container: dagger.Container
    config: YAMLConfig
    repo_root: Optional[str] = "."


async def detect(ctx: RunContext[TestEnvDependencies]) -> str:
    """Detect project environment and test setup."""
    print(blue("🔍 Detecting test environment..."))

    # Read config override
    testing_config = ctx.deps.config.testing if hasattr(
        ctx.deps.config, 'testing') else {}

    # Get directory listing to detect language/framework
    try:
        entries = await ctx.deps.container.directory(ctx.deps.repo_root or ".").entries()
    except Exception:
        entries = []

    cfg = TestEnvConfig()

    # Detection heuristics (first match wins)
    if any(f in entries for f in ["pyproject.toml", "pytest.ini", "requirements.txt", "uv.lock", "poetry.lock"]):
        cfg.language = "python"
        cfg.framework = "pytest"
        if "uv.lock" in entries:
            cfg.package_manager = "uv"
            cfg.install_command = "uv pip install -r requirements.txt"
        elif "poetry.lock" in entries:
            cfg.package_manager = "poetry"
            cfg.install_command = "poetry install"
        else:
            cfg.package_manager = "pip"
            cfg.install_command = "pip install -r requirements.txt"
        cfg.test_command = "pytest -q"
    elif "package.json" in entries:
        cfg.language = "node"
        cfg.framework = "jest"  # default assumption
        if "pnpm-lock.yaml" in entries:
            cfg.package_manager = "pnpm"
            cfg.install_command = "pnpm install --frozen-lockfile"
        elif "yarn.lock" in entries:
            cfg.package_manager = "yarn"
            cfg.install_command = "yarn install --frozen-lockfile"
        elif "bun.lockb" in entries:
            cfg.package_manager = "bun"
            cfg.install_command = "bun install"
        else:
            cfg.package_manager = "npm"
            cfg.install_command = "npm ci"
        cfg.test_command = "npm test --silent"
    elif "go.mod" in entries:
        cfg.language = "go"
        cfg.framework = "go test"
        cfg.package_manager = "go"
        cfg.test_command = "go test ./..."
        cfg.needs_install = False
    elif "pom.xml" in entries:
        cfg.language = "java"
        cfg.framework = "maven"
        cfg.package_manager = "mvn"
        cfg.test_command = "mvn -q -DskipTests=false test"
        cfg.install_command = "mvn compile test-compile"
    elif "Cargo.toml" in entries:
        cfg.language = "rust"
        cfg.framework = "cargo"
        cfg.package_manager = "cargo"
        cfg.test_command = "cargo test --quiet"
        cfg.needs_install = False
    elif any(f in entries for f in ["deno.json", "deno.jsonc"]):
        cfg.language = "deno"
        cfg.framework = "deno"
        cfg.package_manager = "deno"
        cfg.test_command = "deno test -A"
        cfg.needs_install = False
    else:
        cfg.skip_tests = True
        cfg.notes = "No recognized language/framework detected"

    # Apply config overrides
    if hasattr(testing_config, 'get'):
        cfg.working_dir = testing_config.get("working_dir") or cfg.working_dir
        cfg.test_command = testing_config.get(
            "test_command") or cfg.test_command
        cfg.install_command = testing_config.get(
            "install_command") or cfg.install_command
        cfg.timeout_seconds = testing_config.get(
            "timeout_seconds") or cfg.timeout_seconds
        if not testing_config.get("enable", True):
            cfg.skip_tests = True

    if not cfg.notes:
        cfg.notes = f"Detected {cfg.language}/{cfg.framework} with {cfg.package_manager}"

    print(
        green(f"✅ Detected: {cfg.language or 'unknown'}/{cfg.framework or 'none'}"))
    return cfg.model_dump_json()


async def configure(ctx: RunContext[TestEnvDependencies], cfg_json: str) -> dagger.Container:
    """Configure container for testing based on TestEnvConfig."""
    print(blue("⚙️ Configuring test environment..."))

    try:
        cfg = TestEnvConfig.model_validate_json(cfg_json)
    except Exception as e:
        print(yellow(f"⚠️ Failed to parse config: {e}"))
        return ctx.deps.container

    container = ctx.deps.container

    if cfg.skip_tests or not cfg.needs_install or not cfg.install_command:
        cfg.configured = True
        print(green("✅ No installation needed"))
    else:
        try:
            work_dir = cfg.working_dir or "."
            print(blue(f"📦 Installing dependencies: {cfg.install_command}"))
            container = container.with_exec([
                "bash", "-lc", f"cd {work_dir} && {cfg.install_command}"
            ])
            cfg.configured = True
            print(green("✅ Dependencies installed"))
        except Exception as e:
            print(yellow(f"⚠️ Install failed: {e}"))
            cfg.configured = False

    # Persist test env config and log
    try:
        container = await write_json(container, "test_env.json", cfg.model_dump())
        log_msg = f"test_env: {cfg.language}/{cfg.framework} pm={cfg.package_manager} configured={cfg.configured}"
        container = await append_log(container, log_msg)
    except Exception:
        pass

    return container


async def get_test_command(ctx: RunContext[TestEnvDependencies], cfg_json: str) -> str:
    """Return the test command for the given configuration."""
    try:
        cfg = TestEnvConfig.model_validate_json(cfg_json)
    except Exception:
        return "echo 'No test command available'"

    if cfg.skip_tests or not cfg.test_command:
        return "echo 'Tests skipped (no test command)'"

    work_dir = cfg.working_dir or "."
    if work_dir != ".":
        return f"cd {work_dir} && {cfg.test_command}"
    return cfg.test_command


def create_test_env_agent(model: OpenAIChatModel) -> Agent:
    """Create the test environment configurator agent."""
    system_prompt = """
You are a Test Environment Configurator Agent.

Your role:
- Detect project language, framework, and package manager
- Configure containers for testing
- Provide appropriate test commands for different environments

Supported environments:
- Python (pytest, uv/poetry/pip)
- Node.js (jest/vitest, npm/yarn/pnpm/bun)
- Go (go test)
- Java (Maven/Gradle)
- Rust (cargo test)
- Deno (deno test)

Always respect configuration overrides and provide clear feedback.
"""

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=TestEnvDependencies,
        retries=2
    )

    agent.tool(detect)
    agent.tool(configure)
    agent.tool(get_test_command)

    print(f"Test Environment Agent created with model: {model.model_name}")
    return agent
