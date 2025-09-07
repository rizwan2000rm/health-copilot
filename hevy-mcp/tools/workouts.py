from typing import Any, Optional
import sys
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request
from .types import (
    WorkoutsResponse,
    Workout,
    WorkoutCountResponse,
    WorkoutEventsResponse,
    CreateWorkoutRequest,
    UpdateWorkoutRequest,
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
        pageSize: Items per page (1..10). Default: 5.

    Returns:
        JSON string of raw API response (no response validation).

    Validation:
        - Requires `HEVY_API_KEY`.
        - `page >= 1`, `1 <= pageSize <= 10`.

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

    # Validate response with Pydantic model
    try:
        validated_response = WorkoutsResponse(**result)
        formatted_workouts = []
        for i, workout in enumerate(validated_response.workouts, 1):
            formatted_workout = f"Workout {i}:\n{workout.model_dump()}"
            formatted_workouts.append(formatted_workout)
        return "\n\n---\n\n".join(formatted_workouts)
    except Exception as e:
        # If validation fails, fall back to original formatting
        formatted_workouts = []
        for i, workout in enumerate(result["workouts"], 1):
            formatted_workout = f"Workout {i}:\n{workout}"
            formatted_workouts.append(formatted_workout)
        return f"Warning: Response validation failed ({e}). Raw response:\n\n" + "\n\n---\n\n".join(formatted_workouts)


@mcp.tool()
async def get_workout(workoutId: WorkoutID) -> str:
    """Get a single workout by ID.

    Args:
        workoutId: Workout UUID.

    Returns:
        JSON string of the full workout including exercises, sets, and metadata.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `workoutId` must resemble a UUID.

    Example:
        get_workout("c1f1e7b6-7a1a-4f8c-9baf-2a6c6b6b9a22")

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
    
    # Validate response with Pydantic model
    try:
        validated_response = Workout(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def create_workout(payload: CreateWorkoutRequest) -> str:
    """Create a workout.

    Args:
        payload: A `CreateWorkoutRequest` with top-level `workout` object.
            - Required: `workout.title` or `workout.name` (string)
            - Optional: `workout.description`, `workout.start_time`, `workout.end_time`, 
              `workout.is_private`, `workout.exercises` (with sets)

    Returns:
        JSON string of the created workout, or raw API payload on validation fallback.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `workout` object required; `workout.title` or `workout.name` required.

    Example:
        {"workout": {"title": "Morning Push", "description": "Upper body workout"}}

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts"
    # Convert Pydantic model to dict for API request
    payload_dict = payload.model_dump()
    result = await make_hevy_request(url, method="POST", payload=payload_dict)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = Workout(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def update_workout(workoutId: WorkoutID, payload: UpdateWorkoutRequest) -> str:
    """Update a workout by ID.

    Args:
        workoutId: Workout UUID.
        payload: `UpdateWorkoutRequest` with a top-level partial `workout`.

    Returns:
        JSON string of the updated workout, or raw API payload on validation fallback.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `workoutId` must resemble a UUID.
        - `workout` object required; include only fields you want to change.

    Example:
        {"workout": {"name": "Upper Body - Week 2", "notes": "Felt strong"}}

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )
    url = f"{API_BASE}/workouts/{workoutId}"
    # Convert Pydantic model to dict for API request
    payload_dict = payload.model_dump()
    result = await make_hevy_request(url, method="PUT", payload=payload_dict)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = Workout(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_workouts_count() -> str:
    """Get the total number of workouts for the account.

    Returns:
        JSON string with `{"count": <int>}`.

    Validation:
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
    
    # Validate response with Pydantic model
    try:
        validated_response = WorkoutCountResponse(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_workout_events(page: PageNumber = 1, pageSize: PageSize = 10, since: Optional[ISODateTime] = None) -> str:
    """List workout events (paged) with optional time filter.

    Args:
        page: Page number (>= 1). Default: 1.
        pageSize: Items per page (1..50). Default: 10.
        since: Optional ISO8601 timestamp to filter events since.

    Returns:
        JSON string of events page, or raw API payload on validation fallback.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `page >= 1`, `1 <= pageSize <= 50`.

    Example:
        get_workout_events(since="2025-01-01T00:00:00Z")

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
    
    # Validate response with Pydantic model
    try:
        validated_response = WorkoutEventsResponse(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


