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
    """Get workouts for a user.

    Args:
        page: Page number (default: 1, must be 1 or greater)
        pageSize: Number of workouts per page (default: 5, max: 10)
        
    Note: Most users only need the first page with default pageSize=5.
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
        workoutId: The workout ID (UUID format)
        
    Returns: Complete workout details including exercises, sets, and metadata.
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
    """Create a new workout.

    Args:
        payload: Must include top-level `workout` object with:
            - name: string (required)
            - date: string (optional, ISO8601 format)
            - notes: string (optional)
            - exercises: array (optional)
            
    Example payload:
        {"workout": {"name": "Morning Workout", "notes": "Felt great today!"}}
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
        workoutId: The workout ID (UUID format)
        payload: Must include top-level `workout` object with fields to update:
            - name: string (optional)
            - date: string (optional, ISO8601 format)
            - notes: string (optional)
            - exercises: array (optional)
            
    Example payload:
        {"workout": {"name": "Updated Workout", "notes": "New notes"}}
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
    """Get the total number of workouts on the account."""
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
    """Get a paged list of workout events since a given date.

    Args:
        page: Page number (default: 1, must be 1 or greater)
        pageSize: Page size (default: 10, max: 50)
        since: ISO8601 timestamp to filter events since (optional)
        
    Note: Most users only need the first page with default pageSize=10.
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


