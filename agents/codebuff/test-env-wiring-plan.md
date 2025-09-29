Title: Wire TestEnv Configurator into Codebuff main and Orchestrator

1) Add proxies in Codebuff main (agents/codebuff/src/codebuff/main.py)
- Add three @function methods to call the TestEnv agent tools (constructor-first, mock-safe config_file):

```py
# ... existing code ...
from .test_env.agent import create_test_env_agent, TestEnvDependencies

@function
async def detect_test_env(self, container: dagger.Container) -> str:
    # returns TestEnvConfig JSON string
    agent = create_test_env_agent(create_llm_model(self.config))  # or reuse existing model var if present
    deps = TestEnvDependencies(
        container=container,
        config=YAMLConfig(**self.config),
        config_file=getattr(self, 'config_file', None),
    )
    result = await agent.run('Call detect tool and return raw JSON.', deps=deps)
    return result.output

@function
async def configure_test_env(self, container: dagger.Container, cfg_json: str) -> dagger.Container:
    agent = create_test_env_agent(create_llm_model(self.config))
    deps = TestEnvDependencies(
        container=container,
        config=YAMLConfig(**self.config),
        config_file=getattr(self, 'config_file', None),
    )
    result = await agent.run(f"Call configure tool with cfg_json='{cfg_json}' and return container", deps=deps)
    return deps.container  # configure returns mutated container in deps

@function
async def get_test_command(self, cfg_json: str) -> str:
    agent = create_test_env_agent(create_llm_model(self.config))
    deps = TestEnvDependencies(
        container=dag.container().from_('alpine:3.20'),  # not used
        config=YAMLConfig(**self.config),
        config_file=getattr(self, 'config_file', None),
    )
    result = await agent.run(f"Call get_test_command tool with cfg_json='{cfg_json}' and return the command only", deps=deps)
    return result.output
```

2) Extend OrchestratorDependencies (agents/codebuff/src/codebuff/orchestrator/models.py)
- Add optional `test_env_cfg_json: Optional[str] = None` and `test_command: Optional[str] = None`.

```py
class OrchestratorDependencies(BaseModel):
    # ... existing fields ...
    test_env_cfg_json: Optional[str] = None
    test_command: Optional[str] = None
```

3) Pass detected test env from main into orchestrator deps (agents/codebuff/src/codebuff/main.py)
- Before creating `deps = OrchestratorDependencies(...)`, detect & configure:

```py
cfg_json = await self.detect_test_env(container)
container = await self.configure_test_env(container, cfg_json)
cmd = await self.get_test_command(cfg_json)

deps = OrchestratorDependencies(
    # ... existing args ...
    test_env_cfg_json=cfg_json,
    test_command=cmd if cmd and 'skip' not in cmd else None,
)
```

4) Use deps.test_command in execute_implementation (agents/codebuff/src/codebuff/orchestrator/agent.py)
- Replace the inline heuristic block with:

```py
# Decide test command
test_cmd = getattr(ctx.deps, 'test_command', None)
if not test_cmd:
    tests_passed = True
    test_output = '\n(tests skipped: no test command)\n'
else:
    # run and handle 'no tests collected' soft-pass
    try:
        run = ctx.deps.container.with_exec(['bash','-lc', test_cmd])
        test_output = await run.stdout()
        tests_passed = True
    except Exception as e:
        msg = str(e)
        if 'collected 0 items' in (test_output or '') or 'collected 0 items' in msg or 'exit code: 5' in msg:
            tests_passed = True
            test_output = (test_output or '') + '\n(no tests collected; treating as success)'
        else:
            tests_passed = False
            test_output = msg
```

5) Persist TestEnvConfig (already handled in configurator)
- TestEnv.configure writes .codebuff-state/test_env.json and a log line

6) Unit tests
- Add a test that mocks detect_test_env/get_test_command to return a Node config and verify execute_implementation uses it and persists test_results.json with tests_passed true when command returns success.

7) Doc
- Update knowledge.md "Test Environment Configurator pattern" with the dependency propagation and soft-pass behavior.
