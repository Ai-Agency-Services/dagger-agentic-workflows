from openai import OpenAI
from typing import List
import dagger


async def generate_embeddings(
    text: str,
    openai_api_key: dagger.Secret,
    model: str = "text-embedding-3-small",
) -> List[float]:
    """
    Generate embeddings for the given text using OpenAI API.
    """
    try:
        # Get the plaintext API key
        api_key = await openai_api_key.plaintext()

        if not api_key:
            print("Warning: OpenAI API key is None or empty")
            return [0.0] * 1536  # Return fallback

        # Initialize the OpenAI client
        client = OpenAI(api_key=api_key)

        # Make the API call - no await needed with synchronous client
        response = client.embeddings.create(
            model=model,
            input=text
        )

        # Check for valid response
        if not response or not hasattr(response, 'data') or not response.data:
            print("Warning: Invalid response from OpenAI embeddings API")
            return [0.0] * 1536

        # Extract the embedding
        return response.data[0].embedding

    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return [0.0] * 1536
