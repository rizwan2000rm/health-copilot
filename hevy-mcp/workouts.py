from typing import Any
import os
import signal
import sys
import httpx
from mcp.server.fastmcp import FastMCP
import json

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

async def make_hevy_request(
    url: str,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Make a request to the Hevy API with proper error handling.

    Args:
        url: Full request URL
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        params: Query parameters
        payload: JSON body for non-GET requests
    """
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
    data = await make_hevy_request(url, method="GET", params=params)

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

@mcp.tool()
async def get_workout(workoutId: str) -> str:
    """Get a single workout by ID.

    Args:
        workoutId: The ID of the workout
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/{workoutId}"
    data = await make_hevy_request(url, method="GET")
    if not data:
        return f"Unable to fetch workout {workoutId}."
    return json.dumps(data, indent=2)

@mcp.tool()
async def create_workout(payload: dict[str, Any]) -> str:
    """Create a new workout.

    Args:
        payload: JSON body per Hevy API spec for creating a workout. Must
            include a top-level `workout` object, for example:
            {
              "workout": {
                "title": "Friday Leg Day 🔥",
                "description": "Medium intensity leg day focusing on quads.",
                "start_time": "2024-08-14T12:00:00Z",
                "end_time": "2024-08-14T12:30:00Z",
                "is_private": false,
                "exercises": [
                  {
                    "exercise_template_id": "D04AC939",
                    "superset_id": null,
                    "notes": "Felt good today. Form was on point.",
                    "sets": [
                      {
                        "type": "normal",
                        "weight_kg": 100,
                        "reps": 10,
                        "distance_meters": null,
                        "duration_seconds": null,
                        "custom_metric": null,
                        "rpe": null
                      }
                    ]
                  }
                ]
              }
            }
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    if not isinstance(payload, dict) or "workout" not in payload or not isinstance(payload["workout"], dict):
        return (
            "Invalid request body. Expected a JSON object with top-level 'workout' key. "
            "See Hevy Workouts create spec."
        )
    url = f"{API_BASE}/workouts"
    data = await make_hevy_request(url, method="POST", payload=payload)
    if not data:
        return "Unable to create workout."
    return json.dumps(data, indent=2)

@mcp.tool()
async def update_workout(workoutId: str, payload: dict[str, Any]) -> str:
    """Update a workout by ID.

    Args:
        workoutId: The ID of the workout
        payload: JSON body with fields to update
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/{workoutId}"
    data = await make_hevy_request(url, method="PUT", payload=payload)
    if not data:
        return f"Unable to update workout {workoutId}."
    return json.dumps(data, indent=2)

@mcp.tool()
async def get_workouts_count() -> str:
    """Get the total number of workouts on the account."""
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/count"
    data = await make_hevy_request(url, method="GET")
    if not data:
        return "Unable to fetch workouts count."
    return json.dumps(data, indent=2)

@mcp.tool()
async def get_workout_events(page: int = 1, pageSize: int = 50, since: str | None = None) -> str:
    """Get a paged list of workout events since a given date.

    Args:
        page: Page number
        pageSize: Page size
        since: ISO8601 timestamp to filter events since
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/events"
    params: dict[str, Any] = {"page": page, "pageSize": pageSize}
    if since:
        params["since"] = since
    data = await make_hevy_request(url, method="GET", params=params)
    if not data:
        return "Unable to fetch workout events."
    return json.dumps(data, indent=2)

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