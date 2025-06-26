from typing import NamedTuple, Optional

import dagger
from dagger import object_type


@object_type
class LLMCredentials(NamedTuple):
    """Holds the base URL and API key for an LLM provider."""
    base_url: Optional[str]
    api_key: dagger.Secret
