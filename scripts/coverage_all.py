#!/usr/bin/env python3
"""Generate coverage report for entire dagger-agents repository."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: list[str], cwd: Path = None) -> int:
    """Run a command and return exit code."""
    print(f"Running: {' '.join(cmd)} (in {cwd or 'current dir'})")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return 1

def main():
    project_root = Path.cwd()
    
    # Modules to test with coverage
    modules = [
        ("services/neo", "neo"),
        ("services/query", "query"), 
        ("workflows/index", "index"),
        ("workflows/graph", "graph"),
        ("workflows/smell", "smell"),
        ("agents/codebuff", "codebuff"),
        ("shared/agent-utils", "agent_utils"),
    ]
    
    print("🔍 Running coverage for all modules...")
    
    # Create coverage directory
    coverage_dir = project_root / "coverage-reports"
    coverage_dir.mkdir(exist_ok=True)
    
    all_passed = True
    
    for module_path, module_name in modules:
        module_dir = project_root / module_path
        if not module_dir.exists():
            print(f"⚠️ Skipping {module_name} - directory not found")
            continue
            
        print(f"\n📊 Testing {module_name}...")
        
        # Run pytest with coverage for this module
        cmd = [
            "uv", "run", "--extra", "test", "pytest", 
            "tests/",
            f"--cov={module_name}",
            "--cov-report=xml:coverage.xml",
            "--cov-report=html:htmlcov",
            "--tb=short",
            "-q"
        ]
        
        exit_code = run_command(cmd, module_dir)
        
        if exit_code == 0:
            print(f"✅ {module_name} tests passed")
            
            # Copy coverage files with module prefix
            if (module_dir / "coverage.xml").exists():
                subprocess.run([
                    "cp", 
                    str(module_dir / "coverage.xml"),
                    str(coverage_dir / f"{module_name}-coverage.xml")
                ])
            
            if (module_dir / "htmlcov").exists():
                subprocess.run([
                    "cp", "-r",
                    str(module_dir / "htmlcov"),
                    str(coverage_dir / f"{module_name}-htmlcov")
                ])
        else:
            print(f"❌ {module_name} tests failed")
            all_passed = False
    
    # Run root tests
    print(f"\n📊 Testing root tests...")
    cmd = [
        "uv", "run", "pytest", "tests/",
        "--cov=tests",
        "--cov-report=xml:root-coverage.xml", 
        "--cov-report=html:root-htmlcov",
        "--tb=short",
        "-q"
    ]
    
    exit_code = run_command(cmd, project_root)
    if exit_code == 0:
        print("✅ Root tests passed")
    else:
        print("❌ Root tests failed")
        all_passed = False
    
    print(f"\n📄 Coverage reports saved to: {coverage_dir}")
    print("\n📋 Summary:")
    
    # List all coverage files
    for coverage_file in coverage_dir.glob("*coverage*"):
        print(f"  • {coverage_file.name}")
    
    if all_passed:
        print("\n🎉 All tests passed with coverage!")
        return 0
    else:
        print("\n⚠️ Some tests failed, but coverage was still generated.")
        return 1

if __name__ == "__main__":
    sys.exit(main())