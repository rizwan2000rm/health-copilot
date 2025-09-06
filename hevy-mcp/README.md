# Hevy MCP Server

A Model Context Protocol (MCP) server for interacting with the Hevy fitness app API. This server provides comprehensive tools for managing workouts, routines, exercises, and webhooks with full type safety and validation.

## Features

- **Complete API Coverage**: All Hevy API endpoints are supported
- **Type Safety**: Full Pydantic model validation for all requests and responses
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Documentation**: All functions include detailed docstrings with examples
- **Validation**: Automatic validation of API responses with fallback to raw responses

## Available Tools

### Workouts

- `get_workouts` - Get paginated list of workouts
- `get_workout` - Get a single workout by ID
- `create_workout` - Create a new workout
- `update_workout` - Update an existing workout
- `get_workouts_count` - Get total workout count
- `get_workout_events` - Get workout events with optional date filtering

### Routines

- `get_routines` - Get paginated list of routines
- `get_routine` - Get a single routine by ID
- `create_routine` - Create a new routine
- `update_routine` - Update an existing routine
- `get_routine_folders` - Get routine folders
- `create_routine_folder` - Create a new routine folder
- `get_routine_folder` - Get a routine folder by ID

### Exercises

- `get_exercise_templates` - Get available exercise templates
- `get_exercise_template` - Get a single exercise template by ID
- `get_exercise_history` - Get exercise history with optional date filtering

### Webhooks

- `create_webhook_subscription` - Create a webhook subscription
- `get_webhook_subscription` - Get current webhook subscription
- `delete_webhook_subscription` - Delete webhook subscription

## Type Safety & Validation

This MCP server uses Pydantic models for comprehensive type safety:

- **Request Models**: All function parameters use typed models (e.g., `CreateWorkoutRequest`, `UpdateRoutineRequest`)
- **Response Models**: All API responses are validated against Pydantic models
- **Type Aliases**: Common types like `WorkoutID`, `RoutineID`, `ExerciseTemplateID` for better clarity
- **Automatic Validation**: Responses are automatically validated, with fallback to raw responses if validation fails

### Example Type Definitions

```python
# Request models
class CreateWorkoutRequest(BaseModel):
    workout: Workout = Field(..., description="Workout data")

# Response models
class WorkoutsResponse(HevyResponse):
    workouts: List[Workout]
    page: int
    page_size: int
    total: Optional[int] = None

# Type aliases
WorkoutID = str
RoutineID = str
ExerciseTemplateID = str
```

## Configuration

Set `HEVY_API_KEY` in your MCP client configuration so it is available in the server process environment. The server reads `HEVY_API_KEY` from `os.environ` and sends it as the `api-key` header on requests.

### Example Configuration

```json
{
  "mcpServers": {
    "hevy": {
      "command": "python",
      "args": ["/path/to/hevy-mcp/app.py"],
      "env": {
        "HEVY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Dependencies

- `httpx>=0.28.1` - HTTP client for API requests
- `mcp[cli]>=1.13.1` - Model Context Protocol framework
- `pydantic>=2.0.0` - Data validation and type safety

## Error Handling

The server provides comprehensive error handling:

- **API Errors**: HTTP status errors are caught and returned as user-friendly messages
- **Validation Errors**: Pydantic validation errors are caught and raw responses are returned with warnings
- **Network Errors**: Request errors are handled gracefully with detailed error messages
- **Missing API Key**: Clear error messages when API key is not configured

## API Reference

For detailed API documentation, see the [Hevy API Documentation](https://api.hevyapp.com/docs/).
