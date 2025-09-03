from typing import Any
import os
import signal
import sys
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("hevy")

# Constants
API_BASE = "https://api.hevyapp.com/v1"
USER_AGENT = "hevy-app/1.0"
API_KEY = os.getenv("HEVY_API_KEY")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("Received shutdown signal, exiting gracefully...", file=sys.stderr)
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def make_hevy_request(url: str, params: dict[str, Any] | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Make a request to the Hevy API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    if API_KEY:
        headers["api-key"] = API_KEY
        print(f"Using API key: {API_KEY[:10]}...", file=sys.stderr)
    else:
        print("No API key provided", file=sys.stderr)
    
    print(f"Making request to: {url}", file=sys.stderr)
    print(f"Headers: {headers}", file=sys.stderr)
    if params:
        print(f"Query params: {params}", file=sys.stderr)
    if payload:
        print(f"Payload: {payload}", file=sys.stderr)
    
    async with httpx.AsyncClient() as client:
        try:
            if payload:
                # Use POST for requests with payload
                headers["Content-Type"] = "application/json"
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            else:
                # Use GET for requests without payload
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            
            print(f"Response status: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {dict(response.headers)}", file=sys.stderr)
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code}: {e.response.text}", file=sys.stderr)
            return None
        except httpx.RequestError as e:
            print(f"Request error: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error in API request: {e}", file=sys.stderr)
            return None

@mcp.tool()
async def get_workouts(page: int = 1, pageSize: int = 10) -> str:
    """Get workouts for a user.

    Args:
        page: Page number (default: 1)
        pageSize: Number of workouts per page (default: 10)
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    
    url = f"{API_BASE}/workouts"
    params = {
        "page": page,
        "pageSize": pageSize
    }
    
    print(f"Making request to {url} with params: {params}", file=sys.stderr)
    data = await make_hevy_request(url, params=params)

    if not data:
        return "Unable to fetch workouts from the API."

    if "workouts" not in data:
        return f"Unexpected API response format: {data}"

    if not data["workouts"]:
        return "No workouts found for this user."

    # Format the workouts nicely
    formatted_workouts = []
    for i, workout in enumerate(data["workouts"], 1):
        formatted_workout = f"Workout {i}:\n{workout}"
        formatted_workouts.append(formatted_workout)

    return "\n\n---\n\n".join(formatted_workouts)

if __name__ == "__main__":
    try:
        # Initialize and run the server
        mcp.run(transport='stdio')
    except BrokenPipeError:
        # Handle broken pipe gracefully when client disconnects
        print("Client disconnected, shutting down gracefully...", file=sys.stderr)
        sys.exit(0)
    except KeyboardInterrupt:
        print("Received interrupt signal, shutting down...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)