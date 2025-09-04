from typing import Any
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request


@mcp.tool()
async def create_webhook_subscription(payload: dict[str, Any]) -> str:
    """Create a new webhook subscription.
    
    Args:
        payload: Must include:
            - url: string (required) - The webhook URL
            - authToken: string (required) - Auth token sent as Authorization header
            
    Example payload:
        {"url": "https://example.com/hevy-webhook", "authToken": "Bearer mytoken"}
        
    Note: Your endpoint must respond with 200 OK within 5 seconds, 
    otherwise delivery will be retried. When a workout is created, 
    you'll receive a POST with: {"id": "...", "payload": {"workoutId": "..."}}
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_webhook_subscription() -> str:
    """Get the current webhook subscription.
    
    Returns: Current webhook details including URL and auth token.
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_webhook_subscription() -> str:
    """Delete the current webhook subscription.
    
    Returns: Confirmation message when successfully deleted.
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
    
    return json.dumps(result, indent=2)
