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
    """List exercise templates (paged).

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
        exerciseTemplateId: Exercise template ID (e.g., "05293BCA").

    Returns:
        JSON string of the template details.

    Validation:
        - Requires `HEVY_API_KEY`.
        - `exerciseTemplateId` required.

    Example:
        get_exercise_template("05293BCA")

    Docs: https://api.hevyapp.com/docs/
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
    """Get exercise history for a template.

    Args:
        exerciseTemplateId: Exercise template ID (e.g., "05293BCA").
        start_date: Optional ISO8601 start.
        end_date: Optional ISO8601 end.

    Returns:
        JSON string with history entries (weights, reps, dates, etc.).

    Validation:
        - Requires `HEVY_API_KEY`.
        - `exerciseTemplateId` required.
        - If both dates provided, `start_date <= end_date`.

    Examples:
        get_exercise_history("05293BCA")
        get_exercise_history("05293BCA", start_date="2024-11-01T00:00:00Z")

    Docs: https://api.hevyapp.com/docs/
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
