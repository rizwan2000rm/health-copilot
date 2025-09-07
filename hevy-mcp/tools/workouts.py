from typing import Any, Optional, Dict
import sys
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request
from .types import (
    WorkoutID,
    PageNumber,
    PageSize,
    ISODateTime
)


@mcp.tool()
async def get_workouts(page: PageNumber = 1, pageSize: PageSize = 5) -> str:
    """List workouts (paged).

    Args:
        page: Page number (>= 1). Default: 1.
        pageSize: Items per page (1..100). Default: 5.

    Returns:
        JSON string of raw API response.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `page >= 1`, `1 <= pageSize <= 100`.

    Example:
        get_workouts()  # first 5 workouts

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/workouts"
    params = {
        "page": page,
        "pageSize": pageSize,
    }

    print(f"Making request to {url} with params: {params}", file=sys.stderr)
    result = await make_hevy_request(url, method="GET", params=params)

    if isinstance(result, tuple):
        return result[1]  # Return error message

    if "workouts" not in result:
        return f"Unexpected API response format: {result}"

    if not result["workouts"]:
        return "No workouts found for this user."

    # Format workouts without validation
    formatted_workouts = []
    for i, workout in enumerate(result["workouts"], 1):
        formatted_workout = f"Workout {i}:\n{json.dumps(workout, indent=2)}"
        formatted_workouts.append(formatted_workout)
    return "\n\n---\n\n".join(formatted_workouts)


@mcp.tool()
async def get_workout(workoutId: WorkoutID) -> str:
    """Get a single workout by ID.

    Args:
        workoutId: Workout UUID.

    Returns:
        JSON string of the full workout including exercises, sets, and metadata.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `workoutId` must resemble a UUID.

    Example:
        get_workout("b459cba5-cd6d-463c-abd6-54f8eafcadcb")

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/{workoutId}"
    result = await make_hevy_request(url, method="GET")
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_workout(payload: Dict[str, Any]) -> str:
    """Create a workout.

    Args:
        payload: Dictionary with top-level `workout` object.
            - Required: `workout.title` (string)
            - Optional: `workout.description`, `workout.start_time`, `workout.end_time`, 
              `workout.is_private`, `workout.exercises` (with sets)

    Returns:
        JSON string of the created workout.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `workout` object required; `workout.title` required.

    Hints for Complex Workouts:
        Before creating complex workouts with exercises, consider fetching:
        - Use `get_exercise_templates()` to find valid exercise_template_id values
        - Use `get_workouts()` to see existing workout structures for reference
        - Use `get_exercise_history()` to check previous performance for specific exercises

    Example:
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
                                "rpe": 8.5
                            }
                        ]
                    }
                ]
            }
        }

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts"
    result = await make_hevy_request(url, method="POST", payload=payload)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_workout(workoutId: WorkoutID, payload: Dict[str, Any]) -> str:
    """Update a workout by ID.

    Args:
        workoutId: Workout UUID.
        payload: Dictionary with a top-level partial `workout`.

    Returns:
        JSON string of the updated workout.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `workoutId` must resemble a UUID.
        - `workout` object required; include only fields you want to change.

    Hints for Complex Updates:
        Before updating workouts with exercises, consider fetching:
        - Use `get_workout(workoutId)` to see the current workout structure
        - Use `get_exercise_templates()` to find valid exercise_template_id values
        - Use `get_exercise_history()` to check previous performance for specific exercises
        - Use `get_workouts()` to see other workout structures for reference

    Example:
        {
            "workout": {
                "title": "Friday Leg Day 🔥",
                "description": "Medium intensity leg day focusing on quads.",
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
                                "rpe": 8.5
                            }
                        ]
                    }
                ]
            }
        }

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/{workoutId}"
    result = await make_hevy_request(url, method="PUT", payload=payload)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_workouts_count() -> str:
    """Get the total number of workouts for the account.

    Returns:
        JSON string with `{"count": <int>}`.

    Requirements:
        - Requires `HEVY_API_KEY`.

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/count"
    result = await make_hevy_request(url, method="GET")
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_workout_events(page: PageNumber = 1, pageSize: PageSize = 10, since: Optional[ISODateTime] = None) -> str:
    """List workout events (paged) with optional time filter.

    Args:
        page: Page number (>= 1). Default: 1.
        pageSize: Items per page (1..50). Default: 10.
        since: Optional ISO8601 timestamp to filter events since.

    Returns:
        JSON string of events page.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `page >= 1`, `1 <= pageSize <= 50`.

    Example:
        get_workout_events(since="2024-01-01T00:00:00Z")

    Docs: https://api.hevyapp.com/docs/
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
    result = await make_hevy_request(url, method="GET", params=params)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


