"""Models for test environment configuration."""

from pydantic import BaseModel
from typing import Optional, Dict


class TestEnvConfig(BaseModel):
    """Configuration for test environment detection and setup."""
    language: Optional[str] = None                 # e.g., "python", "node", "go", "java", "rust"
    framework: Optional[str] = None                # e.g., pytest, jest, vitest, go test, mvn surefire, gradle test, cargo test
    package_manager: Optional[str] = None          # pip/uv/poetry, npm/yarn/pnpm/bun, go, mvn/gradle, cargo
    working_dir: Optional[str] = None              # subdir if monorepo
    install_command: Optional[str] = None          # e.g., "uv pip install -r requirements.txt" or "npm ci"
    test_command: Optional[str] = None             # e.g., "pytest -q" or "npm test --silent"
    env: Dict[str, str] = {}                       # env vars to set for tests
    needs_install: bool = True
    configured: bool = False                       # container prepped for tests
    notes: Optional[str] = None                    # summary of detection
    skip_tests: bool = False                       # true when no tests configured (soft-pass)
    timeout_seconds: Optional[int] = None          # override for long suites
