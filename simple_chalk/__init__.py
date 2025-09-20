# simple_chalk shim for CI: provides no-op color functions
# This module is picked up in CI because PYTHONPATH includes the repo root.
# It is not packaged (root build only includes services/, workflows/, agents/, shared/),
# so production/dev installs can still use the real simple_chalk package.

def _identity(msg):
    return msg

blue = _identity
green = _identity
yellow = _identity
red = _identity
