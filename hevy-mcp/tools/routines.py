from typing import Any
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request


@mcp.tool()
async def get_routines(page: int = 1, pageSize: int = 5) -> str:
    """Get routines (paged). 
    
    Args:
        page: Page number (default: 1, must be 1 or greater)
        pageSize: Number of routines per page (default: 5, max: 10)
        
    Note: Most users only need the first page with default pageSize=5.
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_routine(payload: dict[str, Any]) -> str:
    """Create a new routine. 
    
    Args:
        payload: Must include top-level `routine` object with:
            - title: string (required)
            - folder_id: number or null (optional, defaults to "My Routines")
            - notes: string (optional)
            - exercises: array (optional)
            
    Example payload:
        {"routine": {"title": "My Workout", "notes": "Focus on form"}}
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_routine(routineId: str) -> str:
    """Get a routine by ID.
    
    Args:
        routineId: The routine ID (UUID format)
        
    Returns: Complete routine details including exercises and sets.
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_routine(routineId: str, payload: dict[str, Any]) -> str:
    """Update an existing routine by ID.
    
    Args:
        routineId: The routine ID (UUID format)
        payload: Must include top-level `routine` object with fields to update:
            - title: string (optional)
            - notes: string (optional)
            - exercises: array (optional)
            
    Example payload:
        {"routine": {"title": "Updated Workout", "notes": "New notes"}}
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_routine_folders(page: int = 1, pageSize: int = 5) -> str:
    """Get routine folders (paged).
    
    Args:
        page: Page number (default: 1, must be 1 or greater)
        pageSize: Number of folders per page (default: 5, max: 10)
        
    Note: Most users only need the first page with default pageSize=5.
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_routine_folder(payload: dict[str, Any]) -> str:
    """Create a new routine folder.
    
    Args:
        payload: Must include top-level `routine_folder` object with:
            - title: string (required)
            
    Example payload:
        {"routine_folder": {"title": "Push Pull 🏋️‍♂️"}}
        
    Note: New folders are created at index 0, shifting others down.
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
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_routine_folder(folderId: str) -> str:
    """Get a routine folder by ID.
    
    Args:
        folderId: The folder ID (numeric)
        
    Returns: Complete folder details including title and metadata.
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
    
    return json.dumps(result, indent=2)


