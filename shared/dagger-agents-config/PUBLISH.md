Publish ais-dagger-agents-config v0.1.20

1) Verify version and exports
- Version: 0.1.20 in shared/dagger-agents-config/pyproject.toml
- __version__: 0.1.20 in shared/dagger-agents-config/src/ais_dagger_agents_config/__init__.py
- Exports include SmellConfig, SmellThresholdsConfig, SmellDetectorsConfig

2) Build the package (from repo root or package dir)
- cd shared/dagger-agents-config
- python -m build
  # or with uv
- uv build

3) Publish to PyPI (recommended)
- Ensure env: PYPI_TOKEN is set to a PyPI API token
- Commands:
  - cd shared/dagger-agents-config
  - python -m twine upload -u __token__ -p "$PYPI_TOKEN" dist/*
  # or with uv
  - uv publish --token "$PYPI_TOKEN"

4) Publish to GitHub Packages (alternative)
- Ensure env: GH_PACKAGES_TOKEN is set (with write:packages)
- Set repository/owner coordinates if needed
- Commands (example):
  - cd shared/dagger-agents-config
  - python -m twine upload -u USERNAME -p "$GH_PACKAGES_TOKEN" --repository-url https://upload.pypi.org/legacy/ dist/*
  (or configure a .pypirc for GitHub Packages)

5) Post-publish
- Verify install: pip install ais-dagger-agents-config==0.1.20
- Confirm downstream modules resolve (they already allow >=0.1.0,<0.2.0)
- Optionally tag the repo and update CHANGELOG
