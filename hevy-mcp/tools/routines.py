from typing import Any, Optional
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request
from .types import (
    RoutinesResponse,
    Routine,
    RoutineResponse,
    RoutineFoldersResponse,
    RoutineFolder,
    CreateRoutineRequest,
    UpdateRoutineRequest,
    CreateRoutineFolderRequest,
    RoutineID,
    FolderID,
    PageNumber,
    PageSize
)


@mcp.tool()
async def get_routines(page: PageNumber = 1, pageSize: PageSize = 5) -> str:
    """List routines (paged).

    Args:
        page: Page number (>= 1). Default: 1.
        pageSize: Items per page (1..100). Default: 5.

    Returns:
        JSON string of raw API response (no response validation).

    Validation:
        - Requires `HEVY_API_KEY`.
        - `page >= 1`, `1 <= pageSize <= 100`.

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/routines"
    params: dict[str, Any] = {"page": page, "pageSize": pageSize}
    result = await make_hevy_request(url, method="GET", params=params)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = RoutinesResponse(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def create_routine(payload: CreateRoutineRequest) -> str:
    """Create a routine.

    Args:
        payload: `CreateRoutineRequest` with top-level `routine` object.
            - Required: `routine.title` (string)
            - Optional: `folder_id`, `notes`, `exercises`

    Returns:
        JSON string of the created routine, or raw API payload on validation fallback.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `routine` object required; `routine.title` required.

    Example:
        {
            "routine": {
                "title": "April Leg Day 🔥",
                "folder_id": null,
                "notes": "Focus on form over weight. Remember to stretch.",
                "exercises": [
                    {
                        "exercise_template_id": "D04AC939",
                        "superset_id": null,
                        "rest_seconds": 90,
                        "notes": "Stay slow and controlled.",
                        "sets": [
                            {
                                "type": "normal",
                                "weight_kg": 100,
                                "reps": 10,
                                "rep_range": {"start": 8, "end": 12}
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

    url = f"{API_BASE}/routines"
    # Convert Pydantic model to dict for API request
    payload_dict = payload.model_dump()
    result = await make_hevy_request(url, method="POST", payload=payload_dict)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = Routine(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_routine(routineId: RoutineID) -> str:
    """Get a routine by ID.

    Args:
        routineId: Routine UUID.

    Returns:
        JSON string of the routine including exercises and sets.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `routineId` must resemble a UUID.

    Example:
        get_routine("b459cba5-cd6d-463c-abd6-54f8eafcadcb")

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/routines/{routineId}"
    result = await make_hevy_request(url, method="GET")
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = RoutineResponse(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def update_routine(routineId: RoutineID, payload: UpdateRoutineRequest) -> str:
    """Update a routine by ID.

    Args:
        routineId: Routine UUID.
        payload: `UpdateRoutineRequest` with a top-level partial `routine`.

    Returns:
        JSON string of the updated routine, or raw API payload on validation fallback.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `routineId` must resemble a UUID.
        - `routine` object required; include only fields you want to change.

    Example:
        {
            "routine": {
                "title": "April Leg Day 🔥",
                "notes": "Focus on form over weight. Remember to stretch.",
                "exercises": [
                    {
                        "exercise_template_id": "D04AC939",
                        "superset_id": null,
                        "rest_seconds": 90,
                        "notes": "Stay slow and controlled.",
                        "sets": [
                            {
                                "type": "normal",
                                "weight_kg": 100,
                                "reps": 10,
                                "rep_range": {"start": 8, "end": 12}
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

    url = f"{API_BASE}/routines/{routineId}"
    # Convert Pydantic model to dict for API request
    payload_dict = payload.model_dump()
    result = await make_hevy_request(url, method="PUT", payload=payload_dict)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = Routine(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_routine_folders(page: PageNumber = 1, pageSize: PageSize = 5) -> str:
    """List routine folders (paged).

    Args:
        page: Page number (>= 1). Default: 1.
        pageSize: Items per page (1..100). Default: 5.

    Returns:
        JSON string of raw API response (no response validation).

    Validation:
        - Requires `HEVY_API_KEY`.
        - `page >= 1`, `1 <= pageSize <= 100`.

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/routine_folders"
    params: dict[str, Any] = {"page": page, "pageSize": pageSize}
    result = await make_hevy_request(url, method="GET", params=params)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = RoutineFoldersResponse(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def create_routine_folder(payload: CreateRoutineFolderRequest) -> str:
    """Create a routine folder.

    Args:
        payload: `CreateRoutineFolderRequest` with top-level `routine_folder` object.
            - Required: `routine_folder.title` (string)

    Returns:
        JSON string of the created folder, or raw API payload on validation fallback.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `routine_folder` object required; `title` required.

    Example:
        {"routine_folder": {"title": "Push Pull 🏋️‍♂️"}}

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/routine_folders"
    # Convert Pydantic model to dict for API request
    payload_dict = payload.model_dump()
    result = await make_hevy_request(url, method="POST", payload=payload_dict)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = RoutineFolder(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_routine_folder(folderId: FolderID) -> str:
    """Get a routine folder by ID.

    Args:
        folderId: Numeric folder ID.

    Returns:
        JSON string of the folder including title and metadata.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `folderId` must be a positive integer.

    Example:
        get_routine_folder(42)

    Docs: https://api.hevyapp.com/docs/
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/routine_folders/{folderId}"
    result = await make_hevy_request(url, method="GET")
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = RoutineFolder(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


