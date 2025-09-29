Title: Test Environment Configurator Agent + Orchestrator Integration

1) New agent: TestEnv Configurator (agents/codebuff/src/codebuff/test_env/agent.py)
- Purpose: Detect project environment, determine test/install commands, optionally configure container for testing, and emit a structured TestEnvConfig.
- Inputs:
  - deps: { container: dagger.Container, config: YAMLConfig, config_file?: dagger.File, repo_root?: str }
  - Optional overrides in YAML: testing.enable, testing.test_command, testing.install_command, testing.working_dir, testing.timeout_seconds
- Outputs:
  - JSON (string) with fields: TestEnvConfig

2) Model: TestEnvConfig (agents/codebuff/src/codebuff/test_env/models.py)
```py
from pydantic import BaseModel
from typing import Optional, List, Dict

class TestEnvConfig(BaseModel):
    language: Optional[str]                 # e.g., "python", "node", "go", "java", "rust"
    framework: Optional[str]                # e.g., pytest, jest, vitest, go test, mvn surefire, gradle test, cargo test
    package_manager: Optional[str]          # pip/uv/poetry, npm/yarn/pnpm/bun, go, mvn/gradle, cargo
    working_dir: Optional[str]              # subdir if monorepo
    install_command: Optional[str]          # e.g., "uv pip install -r requirements.txt" or "npm ci"
    test_command: Optional[str]             # e.g., "pytest -q" or "npm test --silent"
    env: Dict[str, str] = {}                # env vars to set for tests
    needs_install: bool = True
    configured: bool = False                # container prepped for tests
    notes: Optional[str]                    # summary of detection
    skip_tests: bool = False                # true when no tests configured (soft-pass)
    timeout_seconds: Optional[int]          # override for long suites
```

3) Agent API (pydantic_ai) in test_env/agent.py
```py
from pydantic_ai import Agent, RunContext
from simple_chalk import blue, green
from .models import TestEnvConfig

@dataclass
class TestEnvDependencies:
    container: dagger.Container
    config: YAMLConfig
    config_file: Optional[dagger.File] = None
    repo_root: Optional[str] = "."

async def detect(ctx: RunContext[TestEnvDependencies]) -> str:
    # Inspect filesystem for language/framework/package manager signals
    # Return TestEnvConfig JSON string

async def configure(ctx: RunContext[TestEnvDependencies], cfg_json: str) -> dagger.Container:
    # Given TestEnvConfig, run install steps in the container if needed
    # Return mutated container

async def get_test_command(ctx: RunContext[TestEnvDependencies], cfg_json: str) -> str:
    # Return the command string to run tests (single shell line)

def create_test_env_agent(model: OpenAIChatModel) -> Agent:
    # System prompt minimal; tools registered: detect, configure, get_test_command
```

4) Detection heuristic (files to check; first match wins with sensible priority)
- Python: pyproject.toml (tool.pytest/poetry), pytest.ini, tox.ini, requirements.txt, uv.lock, poetry.lock
  - pm: uv>poetry>pip; test: "pytest -q"; install: uv pip install -r/poetry install
- Node: package.json (scripts.test), lock: pnpm-lock.yaml>yarn.lock>package-lock.json>bun.lockb
  - pm: pnpm>yarn>npm>bun; test: read scripts.test else jest/vitest defaults; install: pm ci/install
- Go: go.mod → test: "go test ./..."; install: none
- Java: pom.xml (mvn) → "mvn -q -DskipTests=false test"; Gradle (gradlew/gradle) → "./gradlew test"; install: wrapper download handled by tool
- Rust: Cargo.toml → "cargo test --quiet"; install: cargo auto-download
- Deno: deno.json/c.jsonc → "deno task test" or "deno test -A"; install: none if using deno
- Monorepo: detect top-level packages/apps/* and pick working_dir if config.testing.working_dir
- Overrides: YAML testing.* wins over detection

Pseudo-code for detect:
```py
# Walk root dir entries; collect signals
if exists(pyproject) or pytest.ini or requirements.txt: set python
elif exists(package.json): set node and pm by lock priority
elif go.mod: set go
elif pom.xml/gradle: set java
elif Cargo.toml: set rust
elif deno.json: set deno
# Compose TestEnvConfig
if node:
  test_cmd = config.testing.test_command or script('test') or 'npm test --silent'
  install = config.testing.install_command or (pm ci or install)
if python:
  test_cmd = config.testing.test_command or 'pytest -q'
  install = config.testing.install_command or preferred_pm_install
# skip_tests if no test command and no obvious signals
```

5) Container configuration (configure tool)
- If cfg.needs_install and cfg.install_command present:
  - container = container.with_exec(["bash","-lc", f"cd {cfg.working_dir or '.'} && {cfg.install_command}"])
  - configured=True
- Export .codebuff-state/test_env.json and log:
  - write_json("test_env.json", cfg)
  - append_log("test_env: {language}/{framework} pm={package_manager} configured={configured}")

6) Orchestrator integration (agents/codebuff/src/codebuff/orchestrator/agent.py)
- In execute_implementation before tests:
  - test_env_cfg = await codebuff_module.detect_test_env(container=..., ...)
  - container = await codebuff_module.configure_test_env(container=..., cfg_json=test_env_cfg)
  - test_cmd = await codebuff_module.get_test_command(cfg_json=test_env_cfg)
  - If cfg.skip_tests True → soft-pass; else run: container.with_exec(["bash","-lc", f"cd {cfg.working_dir or '.'} && {test_cmd}"])
- Write test_env.json and incorporate notes into implementation/test_results.json
- Remove fixed "pytest -q" branch; use test_cmd computed above

7) Codebuff main wiring (agents/codebuff/src/codebuff/main.py)
- When constructing dependencies for test_env agent, pass config_file (Dagger-safe pattern)
- Add three functions in main that proxy to test_env agent tools (constructor-first style):
```py
@function
async def detect_test_env(self, container: dagger.Container) -> str: ...
@function
async def configure_test_env(self, container: dagger.Container, cfg_json: str) -> dagger.Container: ...
@function
async def get_test_command(self, cfg_json: str) -> str: ...
```

8) YAML config extensions (shared config)
```yaml
testing:
  enable: true
  working_dir: "apps/api"   # optional
  test_command: "pnpm test --filter api"
  install_command: "pnpm install --frozen-lockfile"
  timeout_seconds: 900
```
- Implement: TestEnv Configurator reads self.config.testing and merges into detected cfg.

9) State and PR artifacts
- Always persist test_env.json in .codebuff-state
- implementation/test_results.json should include: { tool: <framework>, test_command, working_dir, tests_passed, test_output }

10) Unit tests
- Test detection for:
  - Python repo (pyproject/pytest.ini)
  - Node repo (package.json with scripts.test and different lockfiles)
  - Go/Java/Rust minimal fixtures (just command strings; no network)
- Test configure: ensure install_command applied (mock container.with_exec)
- Orchestrator unit test: mock test_env tools to return specific cfg and verify execute_implementation runs correct command and persists files

11) Minimal changes to existing agents
- Remove hardcoded pytest path in execute_implementation; replace with test_env result
- Keep previous soft-pass for "no tests collected"; now governed by cfg.skip_tests or lack of test_command

12) Documentation
- knowledge.md under Dagger Integration: "Test Environment Configurator pattern" with dependency flow and YAML overrides
- agents/codebuff/README.md: add a usage section to run detect/configure/get_test_command via CLI

13) Safety and fallbacks
- If detection returns no language and no overrides → cfg.skip_tests True; orchestrator soft-pass with log entry
- Timeouts applied from cfg.timeout_seconds when running tests
- All writes reassign ctx.deps.container and append to .codebuff-state/log.txt
