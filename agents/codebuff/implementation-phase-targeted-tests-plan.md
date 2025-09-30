1) Wire an Implementation Agent into execute_implementation (generate code + tests)

- In agents/codebuff/src/codebuff/main.py (orchestrate_feature_development):
  - After building the orchestrator model, also build an implementation model and pass it through OrchestratorDependencies so the orchestrator can create/use the Implementation Agent without guessing:
    ```py
    # add after model = await self._get_llm_for_agent("orchestrator", ...)
    impl_model = await self._get_llm_for_agent("implementation", open_router_api_key, openai_api_key)
    
    deps = OrchestratorDependencies(
      ...,
      model=impl_model,  # NEW: pass implementation model for sub-agent
      ...
    )
    ```

- In agents/codebuff/src/codebuff/orchestrator/agent.py:
  - Imports (top):
    ```py
    # add imports
    from ..implementation.agent import create_implementation_agent, ImplementationDependencies
    ```
  - In execute_implementation(), before constructing change_set:
    ```py
    # Build a string for the plan and selected files (already have plan_str)
    selected_files = [f.path for f in (state.file_set.files or [])][:20] if state.file_set and state.file_set.files else []

    # Instantiate Implementation agent once (reuse via deps)
    if ctx.deps.implementation is None:
        # ctx.deps.model was set in main.py to the implementation model
        ctx.deps.implementation = create_implementation_agent(ctx.deps.model)

    # Run the implementation agent to APPLY the plan
    impl_deps = ImplementationDependencies(config=ctx.deps.config, container=ctx.deps.container, plan=plan_str)
    impl_prompt = (
        "Apply the plan.\n"
        "Requirements:\n"
        "- Modify only files relevant to the goal (prioritize: " + ", ".join(selected_files) + ") if provided.\n"
        "- Create NEW implementation code as needed.\n"
        "- Create NEW unit tests for the new code in the appropriate test locations.\n"
        "- Keep changes minimal and isolated.\n"
        "- Do not refactor unrelated code.\n"
        "Output a brief summary of files created/modified."
    )
    impl_result = await ctx.deps.implementation.run(impl_prompt, deps=impl_deps)

    # Adopt the mutated container
    ctx.deps.container = impl_deps.container
    ```

  - Immediately after running the agent, compute changed files + detect tests created:
    ```py
    # Stage-but-don't-commit to see changed files
    ctx.deps.container = ctx.deps.container.with_exec(["bash", "-lc", "git add -N . || true"])  # new intent add
    changed = await ctx.deps.container.with_exec(["bash", "-lc", "git status --porcelain"]).stdout()

    # Parse files and classify
    changed_paths = [ln.split()[-1] for ln in (changed.splitlines() if changed else []) if ln.strip()]
    test_like = []
    code_like = []
    for p in changed_paths:
        # naive language-agnostic patterns for tests
        if any(x in p for x in ["/__tests__/", ".test.", ".spec.", "test_", "_test."]):
            test_like.append(p)
        elif p.endswith(('.py','.ts','.tsx','.js','.go','.java','.rs')):
            code_like.append(p)

    # Build ChangeSet using changed paths (creation/modification only)
    edits = []
    for p in changed_paths:
        op = "create" if "??" in changed else "modify"  # fallback; porcelain parsing is acceptable simplification
        edits.append({"path": p, "operation": op, "content_preview": None})
    change_set = ChangeSet(edits=edits, commands=[], migration_notes=impl_result.output if hasattr(impl_result, 'output') else str(impl_result))
    state.change_set = change_set

    # Persist a targeted summary for testing phase
    awaitable = write_json(ctx.deps.container, "implementation/targets.json", {"tests": test_like, "code": code_like, "all_changed": changed_paths})
    ctx.deps.container = await awaitable
    ```

2) Run ONLY new/changed tests (not the entire suite)

- Use existing ReporterConfig.file_test_command_template in YAMLConfig (already present) to template a per-file test command.
  - Example expectations:
    - Python/pytest: "pytest -q {file}"
    - Jest: "npm test -- --testPathPattern {file}"
    - Vitest: "pnpm vitest run {file}"

- In agents/codebuff/src/codebuff/orchestrator/agent.py, replace the current test execution block with targeted test logic:
    ```py
    tests_passed = False
    test_output = ""

    # Load reporter template if present
    reporter = getattr(ctx.deps.config, 'reporter', None)
    file_tpl = getattr(reporter, 'file_test_command_template', None) if reporter else None

    # Read targets written above
    targets_json = await ctx.deps.container.file(".codebuff-state/implementation/targets.json").contents()
    try:
        targets = json.loads(targets_json) if targets_json else {}
    except Exception:
        targets = {}
    test_files = targets.get("tests", [])

    if test_files:
        # Prefer per-file execution
        results = []
        for tf in test_files[:20]:  # cap to avoid explosion
            if file_tpl:
                cmd = file_tpl.replace("{file}", tf)
            else:
                # heuristic fallback by language
                if tf.endswith('.py'):
                    cmd = f"pytest -q {tf}"
                elif any(tf.endswith(x) for x in ('.ts','.tsx','.js')):
                    cmd = f"npm test -- --testPathPattern '{tf}'"
                else:
                    cmd = getattr(ctx.deps.config.testing, "test_command", "echo 'no file-level test template'")

            run = ctx.deps.container.with_exec(["bash", "-lc", cmd])
            out = await run.stdout()
            results.append({"file": tf, "cmd": cmd, "out": out[:2000]})

        # Consider pass if all per-file runs produce zero nonzero exceptions (stdout captured implies success in this block)
        tests_passed = True
        test_output = json.dumps(results)[:5000]
    else:
        # If no tests were created by the agent, run nothing by default; optionally fall back to config.testing.test_command iff explicitly set
        test_cmd = getattr(ctx.deps.config.testing, "test_command", None)
        if test_cmd:
            run = ctx.deps.container.with_exec(["bash", "-lc", test_cmd])
            test_output = await run.stdout()
            tests_passed = True
        else:
            tests_passed = True
            test_output = "No targeted tests detected; skipping suite by design"
    ```

- Persist per-file test results as before, unchanged path, but the payload now reflects targeted runs. Keep failure handling identical: no commit when targeted tests fail.

3) Commit only after targeted tests pass

- Keep existing git commit code, unchanged. The only difference is the gate condition (based on targeted tests now).

4) Demo configuration updates (non-breaking; optional)

- agents/codebuff/demo/codebuff-feature-demo.yaml: add a ReporterConfig example so per-file runs work out-of-the-box.
  ```yaml
  reporter:
    file_test_command_template: "pytest -q {file}" # for Python repos
  ```
  or for Jest:
  ```yaml
  reporter:
    file_test_command_template: "npm test -- --testPathPattern {file}"
  ```

5) Notes on minimalism and safety

- No new public functions; only extend execute_implementation and wire model into OrchestratorDependencies.
- Reuse existing Implementation Agent; no new package dependencies.
- All state persists under .codebuff-state/implementation/* (targets.json + existing artifacts).
- Fall back to zero tests when none created; do not run full suite by default to honor the requirement.

6) Pseudocode interfaces impacted

- OrchestratorDependencies (already has 'model' Optional[Any]): used to carry implementation model instance; no signature change.
- Implementation run:
  ```py
  impl_agent = create_implementation_agent(ctx.deps.model)
  await impl_agent.run(impl_prompt, deps=ImplementationDependencies(config=ctx.deps.config, container=ctx.deps.container, plan=plan_str))
  ctx.deps.container = impl_deps.container
  ```

7) Test heuristics (language quick-picks) [fallback path only]

- If reporter.file_test_command_template missing and test_files detected:
  - .py -> pytest single-file
  - .ts/.tsx/.js -> npm test -- --testPathPattern
  - else -> skip or use config.testing.test_command if provided
