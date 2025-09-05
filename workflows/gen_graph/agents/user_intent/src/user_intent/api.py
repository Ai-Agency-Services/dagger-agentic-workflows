import os
import logging
from typing import Dict, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.ag_ui import StateDeps
from starlette.middleware.cors import CORSMiddleware

from user_intent.core.intent import create_user_intent_agent_with_ag_ui
from user_intent.models import UserIntentState, GraphIntent


# Setup logging
logger = logging.getLogger("user_intent.api")


def create_fastapi_app(model_name: str = "gpt-4o", provider: str = "openai") -> FastAPI:
    """
    Create a FastAPI application serving the UserIntentAgent with AG-UI protocol.

    Args:
        model_name: The name of the model to use (default: gpt-4o)
        provider: The provider to use (default: openai)

    Returns:
        A FastAPI app with the agent mounted at /agent
    """
    app = FastAPI(title="User Intent Agent API")

    # Add CORS middleware to allow requests from any origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Get the API key from the environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = None

    if provider == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        base_url = "https://openrouter.ai/api/v1"

    # Create provider and model
    llm_provider = OpenAIProvider(api_key=api_key, base_url=base_url)
    pydantic_ai_model = OpenAIModel(
        model_name=model_name, provider=llm_provider)

    # Create agent
    agent = create_user_intent_agent_with_ag_ui(
        pydantic_ai_model=pydantic_ai_model)

    # Add a direct endpoint to handle requests
    @app.post("/agent")
    async def agent_endpoint(request: Request) -> Response:
        """Handle user intent requests directly."""
        try:
            # Parse request body
            body = await request.json()

            # Extract message content from the request
            message_content = "Help me create a knowledge graph"
            if "messages" in body and isinstance(body["messages"], list) and body["messages"]:
                first_message = body["messages"][0]
                if isinstance(first_message, dict) and "content" in first_message:
                    message_content = first_message["content"]

            # Create a fresh state for this request
            user_state = UserIntentState()
            deps = StateDeps(state=user_state)

            # Use agent directly for simplicity
            await agent.run(message_content, deps=deps)

            # Check if we have an approved user goal
            result = {}
            if deps.state.approved_user_goal:
                result = {
                    "kind_of_graph": deps.state.approved_user_goal.kind_of_graph,
                    "graph_description": deps.state.approved_user_goal.graph_description
                }
            elif deps.state.perceived_user_goal:
                result = deps.state.perceived_user_goal

            # Return the result as JSON
            return JSONResponse(content=result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process request: {str(e)}"}
            )

    # Add a simple health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "model": model_name, "provider": provider}

    return app


# For direct usage with uvicorn
def get_app() -> FastAPI:
    """
    Get the FastAPI app using environment variables.
    Use: uvicorn user_intent.api:get_app --factory
    """
    model_name = os.environ.get("MODEL_NAME", "gpt-4o")
    provider = os.environ.get("PROVIDER", "openai")
    return create_fastapi_app(model_name=model_name, provider=provider)
