from typing import Any, Optional
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request
from .types import (
    WebhookSubscription,
    CreateWebhookRequest
)


@mcp.tool()
async def create_webhook_subscription(payload: CreateWebhookRequest) -> str:
    """Create a webhook subscription.

    Args:
        payload: `CreateWebhookRequest` with:
            - `url`: webhook URL
            - `authToken`: token echoed as Authorization header

    Returns:
        JSON string of the created subscription.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `url` and `authToken` are required.

    Example:
        {"url": "https://example.com/hevy-webhook", "authToken": "Bearer mytoken"}

    Delivery:
        Your endpoint should return 200 OK within ~5s; otherwise deliveries are retried.
        Example event: {"id": "...", "payload": {"workoutId": "..."}}

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/webhook-subscription"
    # Convert Pydantic model to dict for API request
    payload_dict = payload.model_dump()
    result = await make_hevy_request(url, method="POST", payload=payload_dict)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = WebhookSubscription(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_webhook_subscription() -> str:
    """Get the current webhook subscription.

    Returns:
        JSON string of the current subscription (URL, auth token, timestamps).

    Validation:
        - Requires `HEVY_API_KEY`.

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/webhook-subscription"
    result = await make_hevy_request(url, method="GET")
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = WebhookSubscription(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def delete_webhook_subscription() -> str:
    """Delete the current webhook subscription.

    Returns:
        Confirmation message or empty JSON on success.

    Validation:
        - Requires `HEVY_API_KEY`.

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/webhook-subscription"
    result = await make_hevy_request(url, method="DELETE")
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # For DELETE operations, we typically get a success message or empty response
    return json.dumps(result, indent=2) if result else "Webhook subscription deleted successfully"
