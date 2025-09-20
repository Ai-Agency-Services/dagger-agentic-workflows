#!/usr/bin/env bash
set -euo pipefail

# CI-style local test runner
# - Requires: uv (https://astral.sh/uv)
# - Optional: dagger (for modules with dagger.json)
# Usage:
#   bash scripts/run_tests_local.sh
#   MODULES="services/query agents/codebuff" bash scripts/run_tests_local.sh

ROOT_DIR="$(pwd -P)"
MODULES_DEFAULT=(
  .
  services/neo
  services/query
  workflows/graph
  workflows/index
  workflows/smell
  workflows/cover
  workflows/cover/plugins/reporter
  workflows/cover/plugins/reporter/pytest
  workflows/cover/plugins/reporter/jest
  agents/codebuff
  agents/builder
  agents/pull_request
  shared/agent-utils
)

# Allow overriding modules via env var MODULES (space-separated)
if [[ -n "${MODULES:-}" ]]; then
  # shellcheck disable=SC2206
  MODULES_LIST=(${MODULES})
else
  MODULES_LIST=("${MODULES_DEFAULT[@]}")
fi

# Helpful notice about dependencies
if ! command -v uv >/dev/null 2>&1; then
  echo "[WARN] 'uv' not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
fi
if ! command -v dagger >/dev/null 2>&1; then
  echo "[INFO] 'dagger' not found. Modules with dagger.json will be skipped for 'dagger develop' step." >&2
fi

rc=0
for m in "${MODULES_LIST[@]}"; do
  echo
  echo "================ MODULE: ${m} ================"
  if [[ -f "${m}/pyproject.toml" || -d "${m}/tests" ]]; then
    # Only run when sdk/ is missing (it's a dev-time dependency)
    if [[ -f "${m}/dagger.json" && ! -d "${m}/sdk" ]]; then
      if command -v dagger >/dev/null 2>&1; then
        (cd "${m}" && dagger develop)
      else
        echo "[WARN] Skipping 'dagger develop' for ${m} (dagger not installed)"
      fi
    else
      if [[ -d "${m}/sdk" ]]; then
        echo "[INFO] Detected ${m}/sdk; skipping 'dagger develop'"
      fi
    fi

    echo "[SYNC] ${m}"
    (cd "${m}" && uv sync --extra test || uv sync)

    echo "[TEST] ${m}"
    (
      set +e
      cd "${m}" || exit 1
      PYTHONPATH="${ROOT_DIR}:${PYTHONPATH:-}" \
      uv run pytest \
        -m "not integration and not neo4j and not llm and not dagger and not slow" \
        --maxfail=1 --tb=short -v
      code=$?
      set -e
      # Exit code 5 == no tests collected; do not fail module in that case
      if [[ ${code} -ne 0 && ${code} -ne 5 ]]; then
        rc=${code}
      fi
    )
  else
    echo "[SKIP] ${m} (no pyproject.toml or tests)"
  fi

done

exit ${rc}
