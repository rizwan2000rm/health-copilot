from typing import Any, Optional, Dict
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request


@mcp.tool()
async def create_webhook_subscription(payload: Dict[str, Any]) -> str:
    """Create a webhook subscription.

    Args:
        payload: Dictionary with:
            - `url`: webhook URL
            - `authToken`: token echoed as Authorization header

    Returns:
        JSON string of the created subscription.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `url` and `authToken` are required.

    Hints for Webhook Setup:
        Before creating webhook subscriptions, consider:
        - Use `get_webhook_subscription()` to check if a subscription already exists
        - Ensure your webhook endpoint is accessible and returns 200 OK within ~5s
        - Test your endpoint with sample payloads before creating the subscription
        - Use `get_workout_events()` to understand the event structure you'll receive

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
    result = await make_hevy_request(url, method="POST", payload=payload)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_webhook_subscription() -> str:
    """Get the current webhook subscription.

    Returns:
        JSON string of the current subscription (URL, auth token, timestamps).

    Requirements:
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
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_webhook_subscription() -> str:
    """Delete the current webhook subscription.

    Returns:
        Confirmation message or empty JSON on success.

    Requirements:
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
