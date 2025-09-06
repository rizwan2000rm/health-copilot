from typing import Any, Optional
import json
from .constants import API_BASE, API_KEY
from .common import mcp, make_hevy_request
from .types import (
    ExerciseTemplatesResponse, 
    ExerciseTemplate, 
    ExerciseHistoryResponse,
    ExerciseTemplateID,
    PageNumber,
    PageSize,
    ISODateTime
)


@mcp.tool()
async def get_exercise_templates(page: PageNumber = 1, pageSize: PageSize = 5) -> str:
    """Get exercise templates available on the account.
    
    Args:
        page: Page number (default: 1, must be 1 or greater)
        pageSize: Number of templates per page (default: 5, max: 10)
        
    Note: Most users only need the first page with default pageSize=5.
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/exercise_templates"
    params: dict[str, Any] = {"page": page, "pageSize": pageSize}
    result = await make_hevy_request(url, method="GET", params=params)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = ExerciseTemplatesResponse(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_exercise_template(exerciseTemplateId: ExerciseTemplateID) -> str:
    """Get a single exercise template by ID.
    
    Args:
        exerciseTemplateId: The exercise template ID (e.g., "05293BCA")
        
    Returns: Complete exercise template details including name, category, etc.
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/exercise_templates/{exerciseTemplateId}"
    result = await make_hevy_request(url, method="GET")
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = ExerciseTemplate(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"


@mcp.tool()
async def get_exercise_history(
    exerciseTemplateId: ExerciseTemplateID, 
    start_date: Optional[ISODateTime] = None, 
    end_date: Optional[ISODateTime] = None
) -> str:
    """Get exercise history for a specific exercise template.
    
    Args:
        exerciseTemplateId: The exercise template ID (e.g., "05293BCA")
        start_date: Optional start date for filtering (ISO 8601 format, e.g., "2024-01-01T00:00:00Z")
        end_date: Optional end date for filtering (ISO 8601 format, e.g., "2024-12-31T23:59:59Z")
        
    Returns: List of exercise history entries with weights, reps, dates, etc.
    
    Example: Get all history for bench press
        get_exercise_history("05293BCA")
        
    Example: Get history for last 30 days
        get_exercise_history("05293BCA", start_date="2024-11-01T00:00:00Z")
    """
    if not API_KEY:
        return (
            "HEVY_API_KEY is required. Set it in your MCP client config "
            "so it is available to the server process."
        )

    url = f"{API_BASE}/exercise_history/{exerciseTemplateId}"
    params: dict[str, Any] = {}
    
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    result = await make_hevy_request(url, method="GET", params=params)
    
    if isinstance(result, tuple):
        return result[1]  # Return error message
    
    # Validate response with Pydantic model
    try:
        validated_response = ExerciseHistoryResponse(**result)
        return json.dumps(validated_response.model_dump(), indent=2)
    except Exception as e:
        # If validation fails, return raw response with warning
        return f"Warning: Response validation failed ({e}). Raw response:\n{json.dumps(result, indent=2)}"
