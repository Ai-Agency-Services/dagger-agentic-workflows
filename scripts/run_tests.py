#!/usr/bin/env python3
"""Test runner script for dagger-agents with various options."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path = None) -> int:
    """Run a command and return exit code."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run tests for dagger-agents")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all", "coverage", "neo4j", "llm"],
        default="unit",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--module",
        choices=["neo", "query", "index", "graph", "smell", "cover", "codebuff", "builder", "pull-request", "agent-utils"],
        help="Specific module to test"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fast",
        action="store_true", 
        help="Skip slow tests"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Add type-specific options
    if args.type == "unit":
        cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        cmd.extend(["-m", "integration"])
    elif args.type == "coverage":
        cmd.extend(["--cov", "--cov-report=term-missing", "--cov-report=html"])
    elif args.type == "neo4j":
        cmd.extend(["-m", "neo4j"])
    elif args.type == "llm":
        cmd.extend(["-m", "llm"])
    
    # Add module-specific path
    if args.module:
        if args.module == "neo":
            cmd.append("services/neo/tests/")
        elif args.module == "query":
            cmd.append("services/query/tests/")
        elif args.module == "index":
            cmd.append("workflows/index/tests/")
        elif args.module == "graph":
            cmd.append("workflows/graph/tests/")
        elif args.module == "smell":
            cmd.append("workflows/smell/tests/")
        elif args.module == "codebuff":
            cmd.append("agents/codebuff/tests/")
        elif args.module == "builder":
            cmd.append("agents/builder/tests/")
        elif args.module == "cover":
            cmd.append("workflows/cover/tests/")
        elif args.module == "pull-request":
            cmd.append("agents/pull_request/tests/")
        elif args.module == "agent-utils":
            cmd.append("shared/agent-utils/tests/")
    
    # Run the command
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())