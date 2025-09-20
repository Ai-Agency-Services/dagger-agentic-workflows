#!/usr/bin/env bash
set -euo pipefail

# CI-style local test runner
# - Requires: uv (https://astral.sh/uv)
# - Optional: dagger (for modules with dagger.json)
# Usage:
#   bash scripts/run_tests_local.sh
#   MODULES="services/query agents/codebuff" bash scripts/run_tests_local.sh
#   COVERAGE=0 bash scripts/run_tests_local.sh            # disable per-module coverage
#   AGGREGATE=0 bash scripts/run_tests_local.sh           # skip combining into one report

ROOT_DIR="$(pwd -P)"
MODULES_DEFAULT=(
  # Removed '.' to avoid root-wide sweep that duplicates per-module coverage
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

# Clean previous combined coverage data unless CLEAN=0
CLEAN="${CLEAN:-1}"
if [[ "${CLEAN}" == "1" ]]; then
  rm -f "${ROOT_DIR}/.coverage" "${ROOT_DIR}/.coverage."* "${ROOT_DIR}/coverage.xml" || true
  rm -rf "${ROOT_DIR}/coverage_html" || true
fi

rc=0
PASSED_MODULES=()
NO_TESTS_MODULES=()
FAILED_MODULES=()
COVERAGE_FILES=()

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
      # Coverage per-module enabled by default; set COVERAGE=0 to disable
      COVERAGE="${COVERAGE:-1}"
      if [[ "${COVERAGE}" == "1" ]]; then
        # Scope coverage to this module only to avoid duplicate data across modules
        if [[ -d "src" ]]; then COV_TARGET="src"; else COV_TARGET="."; fi
        COV_ARGS=(--cov="${COV_TARGET}" --cov-config="${ROOT_DIR}/pyproject.toml" --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml)
      else
        COV_ARGS=()
      fi
      if [[ "${COVERAGE}" == "1" ]]; then
        slug="${m//\//-}"
        [[ "${slug}" == "." || -z "${slug}" ]] && slug="root"
        export COVERAGE_FILE="${ROOT_DIR}/.coverage.${slug}"
      fi
      PYTHONPATH="${ROOT_DIR}:${PYTHONPATH:-}" \
      uv run pytest \
        -m "not integration and not neo4j and not llm and not dagger and not slow" \
        --maxfail=1 --tb=short -v "${COV_ARGS[@]}"
      code=$?

      # Record status and clean empty/no-test coverage files
      if [[ ${code} -eq 0 ]]; then
        PASSED_MODULES+=("${m}")
        if [[ "${COVERAGE}" == "1" && -f "${COVERAGE_FILE:-}" && -s "${COVERAGE_FILE}" ]]; then
          # Probe this coverage file; remove if it reports no data
          export COVERAGE_FILE
          probe_out=$(uvx --from coverage coverage report --rcfile "${ROOT_DIR}/pyproject.toml" 2>&1 || true)
          if echo "${probe_out}" | grep -q "No data to report."; then
            rm -f "${COVERAGE_FILE}" || true
          else
            COVERAGE_FILES+=("${COVERAGE_FILE}")
          fi
        fi
      elif [[ ${code} -eq 5 ]]; then
        NO_TESTS_MODULES+=("${m}")
        if [[ "${COVERAGE}" == "1" && -f "${COVERAGE_FILE:-}" ]]; then
          rm -f "${COVERAGE_FILE}" || true
        fi
      else
        FAILED_MODULES+=("${m}")
      fi
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

# Aggregate coverage across modules by default
AGGREGATE="${AGGREGATE:-1}"
if [[ "${AGGREGATE}" == "1" ]]; then
  echo
  echo "================ AGGREGATE COVERAGE ================"
  if compgen -G "${ROOT_DIR}/.coverage.*" >/dev/null; then
    echo "[INFO] Combining the following coverage data files:"
    ls -1 "${ROOT_DIR}/.coverage."* | sed "s#${ROOT_DIR}/##" || true
    uvx --from coverage coverage combine --rcfile "${ROOT_DIR}/pyproject.toml" "${ROOT_DIR}/.coverage."*
    uvx --from coverage coverage html --rcfile "${ROOT_DIR}/pyproject.toml" -d "${ROOT_DIR}/coverage_html"
    uvx --from coverage coverage xml --rcfile "${ROOT_DIR}/pyproject.toml" -o "${ROOT_DIR}/coverage.xml"
    echo "✅ Combined HTML report: ${ROOT_DIR}/coverage_html/index.html"
    echo "✅ Combined XML report:  ${ROOT_DIR}/coverage.xml"
  else
    echo "[INFO] No per-module .coverage.* files found to aggregate"
  fi
fi

# Summary
echo
echo "================ SUMMARY ================"
if ((${#PASSED_MODULES[@]})); then
  echo "✅ Tests passed in:"
  for m in "${PASSED_MODULES[@]}"; do echo "  - $m"; done
fi
if ((${#NO_TESTS_MODULES[@]})); then
  echo "ℹ️  No tests collected in:"
  for m in "${NO_TESTS_MODULES[@]}"; do echo "  - $m"; done
fi
if ((${#FAILED_MODULES[@]})); then
  echo "❌ Tests failed in:"
  for m in "${FAILED_MODULES[@]}"; do echo "  - $m"; done
fi

exit ${rc}
