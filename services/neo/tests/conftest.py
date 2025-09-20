# Ensure shared fixtures are available to services/neo tests
# This loads shared/pytest_plugins/fixtures.py
pytest_plugins = [
    "shared.pytest_plugins.fixtures",
]
