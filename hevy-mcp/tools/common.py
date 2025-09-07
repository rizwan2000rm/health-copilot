from typing import Any, Union, Dict
import sys
import httpx
from mcp.server.fastmcp import FastMCP
from .constants import API_BASE, USER_AGENT, API_KEY


# Initialize FastMCP server for Hevy tools (shared instance)
mcp = FastMCP("hevy")


async def make_hevy_request(
    url: str,
    method: str = "GET",
    params: Dict[str, Any] | None = None,
    payload: Dict[str, Any] | None = None,
) -> Union[Dict[str, Any], tuple[None, str]]:
    """Make a request to the Hevy API with proper error handling.
    
    Args:
        url: The API endpoint URL
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        params: Query parameters for GET requests
        payload: JSON payload for POST/PUT/PATCH requests
        
    Returns:
        Dict[str, Any]: Raw API response data
        tuple[None, str]: (None, error_message) on failure
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if API_KEY:
        # Hevy API expects `api-key` header according to the official spec
        headers["api-key"] = API_KEY
        print(f"Using API key: {API_KEY[:10]}...", file=sys.stderr)
    else:
        print("No API key provided", file=sys.stderr)

    print(f"Making request to: {url}", file=sys.stderr)
    print(f"Headers: {headers}", file=sys.stderr)
    print(f"Method: {method}", file=sys.stderr)
    if params:
        print(f"Query params: {params}", file=sys.stderr)
    if payload:
        print(f"Payload: {payload}", file=sys.stderr)

    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            elif method.upper() == "POST":
                headers["Content-Type"] = "application/json"
                response = await client.post(url, headers=headers, params=params, json=payload, timeout=30.0)
            elif method.upper() == "PUT":
                headers["Content-Type"] = "application/json"
                response = await client.put(url, headers=headers, params=params, json=payload, timeout=30.0)
            elif method.upper() == "PATCH":
                headers["Content-Type"] = "application/json"
                response = await client.patch(url, headers=headers, params=params, json=payload, timeout=30.0)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, params=params, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            print(f"Response status: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {dict(response.headers)}", file=sys.stderr)

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            try:
                # Try to parse JSON error response
                error_json = e.response.json()
                if "error" in error_json:
                    error_message = f"HTTP {e.response.status_code}: {error_json['error']}"
                else:
                    error_message = f"HTTP {e.response.status_code}: {error_text}"
            except:
                # Fallback to text if not JSON
                error_message = f"HTTP {e.response.status_code}: {error_text}"
            
            print(f"HTTP error {e.response.status_code}: {error_text}", file=sys.stderr)
            return None, error_message
        except httpx.RequestError as e:
            error_message = f"Request error: {e}"
            print(f"Request error: {e}", file=sys.stderr)
            return None, error_message
        except Exception as e:
            error_message = f"Unexpected error in API request: {e}"
            print(f"Unexpected error in API request: {e}", file=sys.stderr)
            return None, error_message


