"""
Type definitions for Hevy API data structures.
These provide clear type hints for the MCP server tools.
"""

from typing import Any, Optional, List, Union, Literal, Dict, TypedDict


# Exercise-related type hints
class ExerciseTemplate(TypedDict, total=False):
    """Exercise template model - represents a predefined exercise."""
    id: str  # The exercise template ID
    title: str  # The exercise title
    type: str  # The exercise type
    primary_muscle_group: str  # The primary muscle group of the exercise
    secondary_muscle_groups: List[str]  # The secondary muscle groups of the exercise
    is_custom: bool  # A boolean indicating whether the exercise is a custom exercise


class ExerciseTemplatesResponse(TypedDict, total=False):
    """Response model for exercise templates list."""
    exercise_templates: List[ExerciseTemplate]  # List of exercise templates
    page: int  # Current page number
    page_count: int  # Total number of pages
    pageSize: int  # Number of items per page
    total: int  # Total number of exercise templates


class ExerciseHistoryEntry(TypedDict, total=False):
    """Single exercise history entry."""
    id: str  # History entry ID
    exercise_template_id: str  # Exercise template ID
    workout_id: str  # Workout ID
    date: str  # Exercise date (ISO 8601 format)
    weight: float  # Weight used in kg
    reps: int  # Number of repetitions
    sets: int  # Number of sets
    duration: int  # Duration in seconds
    distance: float  # Distance covered in meters
    notes: str  # Exercise notes


class ExerciseHistoryResponse(TypedDict, total=False):
    """Response model for exercise history."""
    history: List[ExerciseHistoryEntry]  # List of exercise history entries
    exercise_template_id: str  # Exercise template ID
    total: int  # Total number of history entries


# Workout-related type hints
class RepRange(TypedDict, total=False):
    """Range of repetitions for a set (Routine sets)."""
    start: int  # Starting rep count for the range
    end: int  # Ending rep count for the range


SetType = Literal['warmup', 'normal', 'failure', 'dropset']
RPEValue = Literal[6, 7, 7.5, 8, 8.5, 9, 9.5, 10]


class ExerciseSet(TypedDict, total=False):
    """Single exercise set for workouts."""
    index: int  # Index indicating the order of the set
    type: SetType  # The type of the set
    weight_kg: float  # Weight lifted in kilograms
    reps: int  # Number of reps logged for the set
    distance_meters: float  # Number of meters logged for the set
    duration_seconds: int  # Number of seconds logged for the set
    rpe: RPEValue  # RPE (Relative perceived exertion) value logged for the set
    custom_metric: float  # Custom metric logged for the set (Currently only used to log floors or steps for stair machine exercises)


class RoutineExerciseSet(TypedDict, total=False):
    """Single exercise set for routines (includes rep_range)."""
    index: int  # Index indicating the order of the set
    type: SetType  # The type of the set
    weight_kg: float  # Weight lifted in kilograms
    reps: int  # Number of reps logged for the set
    rep_range: RepRange  # Range of reps for the set, if applicable
    distance_meters: float  # Number of meters logged for the set
    duration_seconds: int  # Number of seconds logged for the set
    rpe: RPEValue  # RPE (Relative perceived exertion) value logged for the set
    custom_metric: float  # Custom metric logged for the set (Currently only used to log floors or steps for stair machine exercises)


class WorkoutExercise(TypedDict, total=False):
    """Exercise within a workout."""
    index: int  # Index indicating the order of the exercise in the workout
    title: str  # Title of the exercise
    notes: str  # Notes on the exercise
    exercise_template_id: str  # The id of the exercise template. This can be used to fetch the exercise template
    supersets_id: int  # The id of the superset that the exercise belongs to. A value of null indicates the exercise is not part of a superset
    sets: List[ExerciseSet]  # Exercise sets


class Workout(TypedDict, total=False):
    """Workout model."""
    id: str  # The workout ID
    title: str  # The workout title
    description: str  # The workout description
    start_time: float  # ISO 8601 timestamp of when the workout was recorded to have started
    end_time: float  # ISO 8601 timestamp of when the workout was recorded to have ended
    updated_at: str  # ISO 8601 timestamp of when the workout was last updated
    created_at: str  # ISO 8601 timestamp of when the workout was created
    exercises: List[WorkoutExercise]  # Workout exercises


class WorkoutsResponse(TypedDict, total=False):
    """Response model for workouts list."""
    workouts: List[Workout]  # List of workouts
    page: int  # Current page number
    page_count: int  # Total number of pages
    pageSize: int  # Number of items per page
    total: int  # Total number of workouts


class WorkoutCountResponse(TypedDict, total=False):
    """Response model for workout count."""
    workout_count: int  # Number of workouts


class UpdatedWorkout(TypedDict, total=False):
    """Updated workout event model."""
    type: str  # Indicates the type of the event (updated)
    workout: Workout  # The updated workout


class DeletedWorkout(TypedDict, total=False):
    """Deleted workout event model."""
    type: str  # Indicates the type of the event (deleted)
    id: str  # The unique identifier of the deleted workout
    deleted_at: str  # A date string indicating when the workout was deleted


# WorkoutEvent is now handled as a Union type directly in responses
WorkoutEvent = Union[UpdatedWorkout, DeletedWorkout]


class PaginatedWorkoutEvents(TypedDict, total=False):
    """Response model for paginated workout events."""
    page: int  # The current page number
    page_count: int  # The total number of pages available
    events: List[WorkoutEvent]  # An array of workout events (either updated or deleted)


class WorkoutEventsResponse(TypedDict, total=False):
    """Response model for workout events."""
    events: List[WorkoutEvent]  # List of workout events
    page: int  # Current page number
    page_size: int  # Number of items per page
    total: int  # Total number of events


# Routine-related type hints
class RoutineExercise(TypedDict, total=False):
    """Exercise within a routine."""
    index: int  # Index indicating the order of the exercise in the routine
    title: str  # Title of the exercise
    rest_seconds: int  # The rest time in seconds between sets of the exercise
    notes: str  # Routine notes on the exercise
    exercise_template_id: str  # The id of the exercise template. This can be used to fetch the exercise template
    supersets_id: int  # The id of the superset that the exercise belongs to. A value of null indicates the exercise is not part of a superset
    sets: List[RoutineExerciseSet]  # Exercise sets


class Routine(TypedDict, total=False):
    """Routine model."""
    id: str  # The routine ID
    title: str  # The routine title
    folder_id: int  # The routine folder ID
    updated_at: str  # ISO 8601 timestamp of when the routine was last updated
    created_at: str  # ISO 8601 timestamp of when the routine was created
    exercises: List[RoutineExercise]  # Routine exercises


class RoutinesResponse(TypedDict, total=False):
    """Response model for routines list."""
    routines: List[Routine]  # List of routines
    page: int  # Current page number
    page_count: int  # Total number of pages
    page_size: int  # Number of items per page
    total: int  # Total number of routines


class RoutineResponse(TypedDict, total=False):
    """Response model for a single routine."""
    routine: Routine  # The routine data


class RoutineFolder(TypedDict, total=False):
    """Routine folder model."""
    id: int  # The routine folder ID
    index: int  # The routine folder index. Describes the order of the folder in the list
    title: str  # The routine folder title
    updated_at: str  # ISO 8601 timestamp of when the folder was last updated
    created_at: str  # ISO 8601 timestamp of when the folder was created


class RoutineFoldersResponse(TypedDict, total=False):
    """Response model for routine folders list."""
    routine_folders: List[RoutineFolder]  # List of routine folders
    page: int  # Current page number
    page_count: int  # Total number of pages
    page_size: int  # Number of items per page
    total: int  # Total number of folders


# Webhook-related type hints
class WebhookSubscription(TypedDict, total=False):
    """Webhook subscription model."""
    authToken: str  # The auth token that will be send as Authorization header in the webhook
    url: str  # The webhook URL


# Request payload type hints
class CreateWorkoutRequest(TypedDict, total=False):
    """Request model for creating a workout."""
    workout: Workout  # Workout data


class UpdateWorkoutRequest(TypedDict, total=False):
    """Request model for updating a workout."""
    workout: Workout  # Workout data to update


class CreateRoutineRequest(TypedDict, total=False):
    """Request model for creating a routine."""
    routine: Routine  # Routine data


class UpdateRoutineRequest(TypedDict, total=False):
    """Request model for updating a routine."""
    routine: Routine  # Routine data to update


class CreateRoutineFolderRequest(TypedDict, total=False):
    """Request model for creating a routine folder."""
    routine_folder: RoutineFolder  # Routine folder data


class CreateWebhookRequest(TypedDict, total=False):
    """Request model for creating a webhook subscription."""
    url: str  # The webhook URL
    authToken: str  # The auth token


# Union types for API responses (for type hints only)
HevyAPIResponse = Union[
    ExerciseTemplatesResponse,
    ExerciseTemplate,
    ExerciseHistoryResponse,
    WorkoutsResponse,
    Workout,
    WorkoutCountResponse,
    WorkoutEventsResponse,
    PaginatedWorkoutEvents,
    UpdatedWorkout,
    DeletedWorkout,
    RoutinesResponse,
    Routine,
    RoutineResponse,
    RoutineFoldersResponse,
    RoutineFolder,
    WebhookSubscription,
    Dict[str, Any]  # For error responses or unknown formats
]


# Type aliases for common patterns - used as hints only
WorkoutID = str  # Workout UUID string
RoutineID = str  # Routine UUID string  
ExerciseTemplateID = str  # Exercise template ID string
FolderID = int  # Folder numeric ID
PageNumber = int  # Page number (>= 1)
PageSize = int  # Page size (1-100)
ISODateTime = str  # ISO 8601 date/time string
