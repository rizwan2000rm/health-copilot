from typing import Any, Optional, Dict
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request
from .types import (
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
        JSON string of raw API response.

    Requirements:
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
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_routine(payload: Dict[str, Any]) -> str:
    """Create a routine.

    Args:
        payload: Dictionary with top-level `routine` object.
            - Required: `routine.title` (string)
            - Optional: `folder_id`, `notes`, `exercises`

    Returns:
        JSON string of the created routine.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `routine` object required; `routine.title` required.

    Hints for Complex Routines:
        Before creating complex routines with exercises, consider fetching:
        - Use `get_exercise_templates()` to find valid exercise_template_id values
        - Use `get_routine_folders()` to find valid folder_id values for organization
        - Use `get_routines()` to see existing routine structures for reference
        - Use `get_exercise_history()` to check previous performance for specific exercises

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
    result = await make_hevy_request(url, method="POST", payload=payload)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_routine(routineId: RoutineID) -> str:
    """Get a routine by ID.

    Args:
        routineId: Routine UUID.

    Returns:
        JSON string of the routine including exercises and sets.

    Requirements:
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
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_routine(routineId: RoutineID, payload: Dict[str, Any]) -> str:
    """Update a routine by ID.

    Args:
        routineId: Routine UUID.
        payload: Dictionary with a top-level partial `routine`.

    Returns:
        JSON string of the updated routine.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `routineId` must resemble a UUID.
        - `routine` object required; include only fields you want to change.

    Hints for Complex Updates:
        Before updating routines with exercises, consider fetching:
        - Use `get_routine(routineId)` to see the current routine structure
        - Use `get_exercise_templates()` to find valid exercise_template_id values
        - Use `get_routine_folders()` to find valid folder_id values for organization
        - Use `get_routines()` to see other routine structures for reference
        - Use `get_exercise_history()` to check previous performance for specific exercises

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
    result = await make_hevy_request(url, method="PUT", payload=payload)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_routine_folders(page: PageNumber = 1, pageSize: PageSize = 5) -> str:
    """List routine folders (paged).

    Args:
        page: Page number (>= 1). Default: 1.
        pageSize: Items per page (1..100). Default: 5.

    Returns:
        JSON string of raw API response.

    Requirements:
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
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_routine_folder(payload: Dict[str, Any]) -> str:
    """Create a routine folder.

    Args:
        payload: Dictionary with top-level `routine_folder` object.
            - Required: `routine_folder.title` (string)

    Returns:
        JSON string of the created folder.

    Requirements:
        - Requires `HEVY_API_KEY`.
        - `routine_folder` object required; `title` required.

    Hints for Organization:
        Before creating routine folders, consider fetching:
        - Use `get_routine_folders()` to see existing folder names and avoid duplicates
        - Use `get_routines()` to understand how folders are used for organization

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
    result = await make_hevy_request(url, method="POST", payload=payload)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_routine_folder(folderId: FolderID) -> str:
    """Get a routine folder by ID.

    Args:
        folderId: Numeric folder ID.

    Returns:
        JSON string of the folder including title and metadata.

    Requirements:
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
    
    # Return raw response without validation
    return json.dumps(result, indent=2)


