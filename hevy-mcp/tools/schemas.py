"""
MCP resources for exposing Hevy API schemas.

This module exposes all JSON schema files from the schemas/ directory as MCP resources,
allowing clients to access the API schema definitions for validation and documentation.
"""

import json
import os
from pathlib import Path
from typing import Any

from .common import mcp

# Get the schemas directory path
SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


def _read_schema_file(filename: str) -> dict[str, Any]:
    """Read and parse a JSON schema file.
    
    Args:
        filename: The name of the schema file (e.g., 'workout.json')
        
    Returns:
        Parsed JSON schema as a dictionary
        
    Raises:
        FileNotFoundError: If the schema file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    schema_path = SCHEMAS_DIR / filename
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {filename}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _format_schema_as_text(schema: dict[str, Any], filename: str) -> str:
    """Format a JSON schema as readable text.
    
    Args:
        schema: The parsed JSON schema
        filename: The original filename for context
        
    Returns:
        Formatted text representation of the schema
    """
    return f"""# Hevy API Schema: {filename}

This is the JSON schema definition for the Hevy API {filename.replace('.json', '')} resource.

## Schema Definition

```json
{json.dumps(schema, indent=2)}
```

## Description

This schema defines the structure and validation rules for {filename.replace('.json', '')} objects in the Hevy API.
"""


# Workout Schema Resources
@mcp.resource("hevy://schemas/workout")
def get_workout_schema() -> str:
    """Get the workout JSON schema definition."""
    schema = _read_schema_file("workout.json")
    return _format_schema_as_text(schema, "workout.json")


@mcp.resource("hevy://schemas/updatedWorkout")
def get_updated_workout_schema() -> str:
    """Get the updated workout JSON schema definition."""
    schema = _read_schema_file("updatedWorkout.json")
    return _format_schema_as_text(schema, "updatedWorkout.json")


@mcp.resource("hevy://schemas/deletedWorkout")
def get_deleted_workout_schema() -> str:
    """Get the deleted workout JSON schema definition."""
    schema = _read_schema_file("deletedWorkout.json")
    return _format_schema_as_text(schema, "deletedWorkout.json")


# Routine Schema Resources
@mcp.resource("hevy://schemas/routine")
def get_routine_schema() -> str:
    """Get the routine JSON schema definition."""
    schema = _read_schema_file("routine.json")
    return _format_schema_as_text(schema, "routine.json")


@mcp.resource("hevy://schemas/routineFolder")
def get_routine_folder_schema() -> str:
    """Get the routine folder JSON schema definition."""
    schema = _read_schema_file("routineFolder.json")
    return _format_schema_as_text(schema, "routineFolder.json")


# Exercise Schema Resources
@mcp.resource("hevy://schemas/exerciseTemplate")
def get_exercise_template_schema() -> str:
    """Get the exercise template JSON schema definition."""
    schema = _read_schema_file("exerciseTemplate.json")
    return _format_schema_as_text(schema, "exerciseTemplate.json")


# Request Body Schema Resources
@mcp.resource("hevy://schemas/postWorkoutsRequestBody")
def get_post_workouts_request_body_schema() -> str:
    """Get the POST workouts request body JSON schema definition."""
    schema = _read_schema_file("postWorkoutsRequestBody.json")
    return _format_schema_as_text(schema, "postWorkoutsRequestBody.json")


@mcp.resource("hevy://schemas/postWorkoutsRequestExercise")
def get_post_workouts_request_exercise_schema() -> str:
    """Get the POST workouts request exercise JSON schema definition."""
    schema = _read_schema_file("postWorkoutsRequestExercise.json")
    return _format_schema_as_text(schema, "postWorkoutsRequestExercise.json")


@mcp.resource("hevy://schemas/postWorkoutsRequestSet")
def get_post_workouts_request_set_schema() -> str:
    """Get the POST workouts request set JSON schema definition."""
    schema = _read_schema_file("postWorkoutsRequestSet.json")
    return _format_schema_as_text(schema, "postWorkoutsRequestSet.json")


@mcp.resource("hevy://schemas/postRoutinesRequestBody")
def get_post_routines_request_body_schema() -> str:
    """Get the POST routines request body JSON schema definition."""
    schema = _read_schema_file("postRoutinesRequestBody.json")
    return _format_schema_as_text(schema, "postRoutinesRequestBody.json")


@mcp.resource("hevy://schemas/postRoutinesRequestExercise")
def get_post_routines_request_exercise_schema() -> str:
    """Get the POST routines request exercise JSON schema definition."""
    schema = _read_schema_file("postRoutinesRequestExercise.json")
    return _format_schema_as_text(schema, "postRoutinesRequestExercise.json")


@mcp.resource("hevy://schemas/postRoutinesRequestSet")
def get_post_routines_request_set_schema() -> str:
    """Get the POST routines request set JSON schema definition."""
    schema = _read_schema_file("postRoutinesRequestSet.json")
    return _format_schema_as_text(schema, "postRoutinesRequestSet.json")


@mcp.resource("hevy://schemas/postRoutineFolderRequestBody")
def get_post_routine_folder_request_body_schema() -> str:
    """Get the POST routine folder request body JSON schema definition."""
    schema = _read_schema_file("postRoutineFolderRequestBody.json")
    return _format_schema_as_text(schema, "postRoutineFolderRequestBody.json")


# PUT Request Body Schema Resources
@mcp.resource("hevy://schemas/putRoutinesRequestBody")
def get_put_routines_request_body_schema() -> str:
    """Get the PUT routines request body JSON schema definition."""
    schema = _read_schema_file("putRoutinesRequestBody.json")
    return _format_schema_as_text(schema, "putRoutinesRequestBody.json")


@mcp.resource("hevy://schemas/putRoutinesRequestExercise")
def get_put_routines_request_exercise_schema() -> str:
    """Get the PUT routines request exercise JSON schema definition."""
    schema = _read_schema_file("putRoutinesRequestExercise.json")
    return _format_schema_as_text(schema, "putRoutinesRequestExercise.json")


@mcp.resource("hevy://schemas/putRoutinesRequestSet")
def get_put_routines_request_set_schema() -> str:
    """Get the PUT routines request set JSON schema definition."""
    schema = _read_schema_file("putRoutinesRequestSet.json")
    return _format_schema_as_text(schema, "putRoutinesRequestSet.json")


# Webhook Schema Resources
@mcp.resource("hevy://schemas/webhookRequestBody")
def get_webhook_request_body_schema() -> str:
    """Get the webhook request body JSON schema definition."""
    schema = _read_schema_file("webhookRequestBody.json")
    return _format_schema_as_text(schema, "webhookRequestBody.json")


# Event Schema Resources
@mcp.resource("hevy://schemas/paginatedWorkoutEvents")
def get_paginated_workout_events_schema() -> str:
    """Get the paginated workout events JSON schema definition."""
    schema = _read_schema_file("paginatedWorkoutEvents.json")
    return _format_schema_as_text(schema, "paginatedWorkoutEvents.json")


# Dynamic schema resource for any schema file
@mcp.resource("hevy://schemas/{schema_name}")
def get_schema_by_name(schema_name: str) -> str:
    """Get a JSON schema definition by name.
    
    Args:
        schema_name: The name of the schema file (e.g., 'workout', 'routine')
        
    Returns:
        Formatted text representation of the schema
        
    Raises:
        FileNotFoundError: If the schema file doesn't exist
    """
    # Ensure the filename has .json extension
    if not schema_name.endswith('.json'):
        schema_name += '.json'
    
    schema = _read_schema_file(schema_name)
    return _format_schema_as_text(schema, schema_name)


# List all available schemas
@mcp.resource("hevy://schemas")
def list_all_schemas() -> str:
    """List all available JSON schema files."""
    if not SCHEMAS_DIR.exists():
        return "No schemas directory found."
    
    schema_files = [f.name for f in SCHEMAS_DIR.glob("*.json")]
    schema_files.sort()
    
    if not schema_files:
        return "No JSON schema files found in the schemas directory."
    
    content = "# Available Hevy API Schemas\n\n"
    content += "The following JSON schema files are available as MCP resources:\n\n"
    
    for schema_file in schema_files:
        schema_name = schema_file.replace('.json', '')
        content += f"- **{schema_name}**: `hevy://schemas/{schema_name}`\n"
    
    content += "\n## Usage\n\n"
    content += "You can access any schema using the resource URI format:\n"
    content += "- `hevy://schemas/workout` - Workout schema\n"
    content += "- `hevy://schemas/routine` - Routine schema\n"
    content += "- `hevy://schemas/exerciseTemplate` - Exercise template schema\n"
    content += "- And many more...\n\n"
    content += "These schemas define the structure and validation rules for Hevy API objects."
    
    return content
