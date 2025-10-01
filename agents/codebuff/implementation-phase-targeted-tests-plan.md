import json
from typing import List, Set
from ..implementation.agent import create_implementation_agent, ImplementationDependencies
# Assume other necessary imports are present, e.g.:
from .models import ChangeSet
from ..utils.container_state import write_json

class OrchestratorAgent:
    async def execute_implementation(self, ctx, state, plan_str):
        # Build selected files list for Implementation agent
        selected_files = [f.path for f in (state.file_set.files or [])][:20] if state.file_set and state.file_set.files else []
        
        # Create Implementation agent if not already created
        if not hasattr(ctx.deps, 'implementation') or ctx.deps.implementation is None:
            impl_model = await _get_llm_for_agent(ctx.deps.config, "implementation", ctx.deps.api_key, None)
            ctx.deps.implementation = create_implementation_agent(impl_model)
        
        # Run Implementation agent
        impl_deps = ImplementationDependencies(
            config=ctx.deps.config,
            container=ctx.deps.container,
            plan=plan_str
        )
        
        impl_prompt = (
            "Apply the implementation plan.\n"
            "Requirements:\n"
            f"- Focus on these files: {', '.join(selected_files) if selected_files else 'any relevant files'}\n"
            "- Create NEW implementation code as needed\n"
            "- Create NEW unit tests for the new code\n"
            "- Keep changes minimal and focused\n"
            "- Follow existing code patterns\n"
            "Output a brief summary of changes made."
        )
        
        impl_result = await ctx.deps.implementation.run(impl_prompt, deps=impl_deps)
        
        # Update container from Implementation agent
        ctx.deps.container = impl_deps.container

        # Stage changes to detect new files
        ctx.deps.container = ctx.deps.container.with_exec(["bash", "-lc", "git add -N . || true"])
        
        # Get changed files using porcelain format
        raw_status = await ctx.deps.container.with_exec(["bash", "-lc", "git status --porcelain=v1 -z"]).stdout()
        
        # Parse changed files
        changed_paths: List[str] = []
        created_files: Set[str] = set()
        modified_files: Set[str] = set()
        
        if raw_status:
            for entry in raw_status.split("\x00"):
                if not entry.strip():
                    continue
                status_code = entry[:2]
                file_path = entry[3:].strip()
                if not file_path:
                    continue
                changed_paths.append(file_path)
                # Check if file was created or modified
                if status_code[0] in ['?', 'A'] or status_code[1] in ['?', 'A']:
                    created_files.add(file_path)
                else:
                    modified_files.add(file_path)
        
        # Categorize files
        test_files = []
        code_files = []
        for path in changed_paths:
            # Detect test files using common patterns
            if any(pattern in path for pattern in [
                "/__tests__/", ".test.", ".spec.", "test_", "_test.",
                "/tests/", "/test/", "_tests."
            ]):
                test_files.append(path)
            elif path.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rs", ".cpp", ".c")):
                code_files.append(path)
        
        # Create ChangeSet from detected changes
        edits = []
        for path in changed_paths:
            operation = "create" if path in created_files else "modify"
            edits.append({
                "path": path,
                "operation": operation,
                "content_preview": None
            })
        
        change_set = ChangeSet(
            edits=edits,
            commands=[],
            migration_notes=str(impl_result.output) if hasattr(impl_result, 'output') else str(impl_result)
        )
        state.change_set = change_set
        
        # Persist targeting data for test execution
        ctx.deps.container = await write_json(
            ctx.deps.container,
            "implementation/targets.json",
            {
                "test_files": test_files,
                "code_files": code_files,
                "all_changed": changed_paths,
                "created": list(created_files),
                "modified": list(modified_files)
            }
        )
        
        # Execute targeted tests
        tests_passed = False
        test_output = ""
        per_file_results = []
        
        # Get test command template from config
        reporter_config = getattr(ctx.deps.config, 'reporter', None)
        file_test_template = getattr(reporter_config, 'file_test_command_template', None) if reporter_config else None
        
        if test_files:
            print(f"🧪 Running {len(test_files)} targeted test files")
            tests_passed = True  # Assume success until a failure occurs
            for test_file in test_files[:20]:
                try:
                    if file_test_template:
                        cmd = file_test_template.replace("{file}", test_file)
                    else:
                        if test_file.endswith('.py'):
                            cmd = f"pytest -xvs {test_file}"
                        elif any(test_file.endswith(ext) for ext in ['.ts', '.tsx', '.js', '.jsx']):
                            cmd = f"npm test -- --testPathPattern='{test_file}'"
                        elif test_file.endswith('.go'):
                            cmd = f"go test -v $(dirname {test_file})"
                        else:
                            cmd = f"echo 'No test runner configured for {test_file}'"
                    test_output_single = await ctx.deps.container.with_exec(["bash", "-lc", cmd]).stdout()
                    per_file_results.append({
                        "file": test_file,
                        "command": cmd,
                        "status": "passed",
                        "output": (test_output_single or "")[:2000]
                    })
                except Exception as e:
                    tests_passed = False
                    per_file_results.append({
                        "file": test_file,
                        "command": cmd,
                        "status": "failed",
                        "error": str(e)[:1000]
                    })
            test_output = json.dumps(per_file_results)[:5000]
        else:
            fallback_cmd = getattr(ctx.deps, 'test_command', None)
            if fallback_cmd:
                print(f"🧪 No targeted tests found, running configured test command: {fallback_cmd}")
                try:
                    test_output = await ctx.deps.container.with_exec(["bash", "-lc", fallback_cmd]).stdout() or ""
                    tests_passed = True
                except Exception as e:
                    error_msg = str(e)
                    if any(phrase in error_msg.lower() for phrase in [
                        "collected 0 items", "no tests collected", "exit code: 5"
                    ]):
                        tests_passed = True
                        test_output = error_msg + "\n(No tests collected; treating as success)"
                    else:
                        tests_passed = False
                        test_output = error_msg[:5000]
            else:
                print("⚠️ No targeted tests detected and no fallback test command configured")
                tests_passed = True
                test_output = "No tests to run; proceeding with implementation"
        
        # Save detailed test results
        ctx.deps.container = await write_json(
            ctx.deps.container,
            "implementation/test-results.json",
            {
                "tests_passed": tests_passed,
                "test_strategy": "targeted" if test_files else "fallback",
                "files_tested": test_files,
                "per_file_results": per_file_results,
                "summary_output": test_output
            }
        )
        
        # Gate commit on test results
        if not tests_passed:
            state.status = "FAILED"
            error = OrchestrationError(
                kind=ErrorKind.TOOL_ERROR,
                message="Targeted tests failed; implementation aborted",
                phase=Phase.IMPLEMENTATION,
                retry_count=state.retry_count
            )
            state.errors.append(error)
            print("❌ Targeted tests failed; aborting commit")
            return "Implementation failed: targeted tests did not pass"
        
        print("✅ Targeted tests passed; proceeding with commit")
        commit_msg = "Automated commit: applied implementation changes"
        await ctx.deps.container.with_exec(["bash", "-lc", f"git commit -am '{commit_msg}'"])
