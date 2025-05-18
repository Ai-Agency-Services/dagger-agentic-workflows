import openai
import os
from typing import List, Any, Dict
import asyncio

# TODO: Change to OpenRouter
# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


async def generate_embeddings(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Generate embeddings for the given text using OpenAI API.
    """
    try:
        response = await openai.Embedding.acreate(
            model=model,
            input=text
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        # Return empty embedding vector as fallback
        return [0.0] * 1536  # Default size for OpenAI embeddings
