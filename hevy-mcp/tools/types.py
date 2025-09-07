"""
Type definitions for Hevy API data structures using Pydantic models.
These provide clear type hints and validation for the MCP server.
"""

from typing import Any, Optional, List, Union, Literal, Dict
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
import uuid


# Constants for API limits and constraints
class APIConstants:
    """Constants for API limits and constraints."""
    MAX_PAGE_SIZE = 100
    MIN_PAGE_SIZE = 1
    MIN_PAGE_NUMBER = 1
    MAX_WEIGHT_KG = 1000.0  # Reasonable upper limit for weight
    MAX_DURATION_SECONDS = 86400  # 24 hours in seconds
    MAX_DISTANCE_METERS = 100000.0  # 100km in meters
    MAX_REPS = 10000  # Reasonable upper limit for repetitions


# Base response models
class HevyResponse(BaseModel):
    """Base response model for Hevy API responses."""
    class Config:
        extra = "forbid"  # Strict validation - reject extra fields
        validate_assignment = True
        use_enum_values = True


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type or code")
    message: Optional[str] = Field(None, description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        extra = "forbid"


# Exercise-related models
class ExerciseTemplate(BaseModel):
    """Exercise template model - represents a predefined exercise."""
    id: Optional[str] = Field(None, description="The exercise template ID")
    title: Optional[str] = Field(None, description="The exercise title")
    type: Optional[str] = Field(None, description="The exercise type")
    primary_muscle_group: Optional[str] = Field(None, description="The primary muscle group of the exercise")
    secondary_muscle_groups: Optional[List[str]] = Field(None, description="The secondary muscle groups of the exercise")
    is_custom: Optional[bool] = Field(None, description="A boolean indicating whether the exercise is a custom exercise")
    
    @validator('secondary_muscle_groups', pre=True)
    def validate_secondary_muscle_groups(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v
    
    class Config:
        extra = "forbid"
        validate_assignment = True


class ExerciseTemplatesResponse(HevyResponse):
    """Response model for exercise templates list."""
    exercise_templates: List[ExerciseTemplate] = Field(..., alias="exercise_templates")
    page: int = Field(..., ge=1, description="Current page number")
    page_count: int = Field(..., alias="page_count", ge=1, description="Total number of pages")
    page_size: Optional[int] = Field(None, alias="pageSize", ge=1, le=100, description="Number of items per page")
    total: Optional[int] = Field(None, ge=0, description="Total number of exercise templates")
    
    class Config:
        extra = "forbid"


class ExerciseHistoryEntry(BaseModel):
    """Single exercise history entry."""
    id: str = Field(..., description="History entry ID", min_length=1)
    exercise_template_id: str = Field(..., description="Exercise template ID", min_length=1)
    workout_id: str = Field(..., description="Workout ID", min_length=1)
    date: datetime = Field(..., description="Exercise date")
    weight: Optional[float] = Field(None, ge=0, le=APIConstants.MAX_WEIGHT_KG, description="Weight used in kg")
    reps: Optional[int] = Field(None, ge=0, le=APIConstants.MAX_REPS, description="Number of repetitions")
    sets: Optional[int] = Field(None, ge=0, description="Number of sets")
    duration: Optional[int] = Field(None, ge=0, le=APIConstants.MAX_DURATION_SECONDS, description="Duration in seconds")
    distance: Optional[float] = Field(None, ge=0, le=APIConstants.MAX_DISTANCE_METERS, description="Distance covered in meters")
    notes: Optional[str] = Field(None, description="Exercise notes")
    
    class Config:
        extra = "forbid"


class ExerciseHistoryResponse(HevyResponse):
    """Response model for exercise history."""
    history: List[ExerciseHistoryEntry] = Field(..., description="List of exercise history entries")
    exercise_template_id: str = Field(..., description="Exercise template ID", min_length=1)
    total: Optional[int] = Field(None, ge=0, description="Total number of history entries")
    
    class Config:
        extra = "forbid"


# Workout-related models
class RepRange(BaseModel):
    """Range of repetitions for a set (Routine sets)."""
    start: Optional[int] = Field(None, description="Starting rep count for the range")
    end: Optional[int] = Field(None, description="Ending rep count for the range")
    
    class Config:
        extra = "forbid"


class ExerciseSet(BaseModel):
    """Single exercise set for workouts."""
    index: Optional[int] = Field(None, description="Index indicating the order of the set")
    type: Optional[Literal['warmup', 'normal', 'failure', 'dropset']] = Field(None, description="The type of the set")
    weight_kg: Optional[float] = Field(None, description="Weight lifted in kilograms")
    reps: Optional[int] = Field(None, description="Number of reps logged for the set")
    distance_meters: Optional[float] = Field(None, description="Number of meters logged for the set")
    duration_seconds: Optional[int] = Field(None, description="Number of seconds logged for the set")
    rpe: Optional[Literal[6, 7, 7.5, 8, 8.5, 9, 9.5, 10]] = Field(None, description="RPE (Relative perceived exertion) value logged for the set")
    custom_metric: Optional[float] = Field(None, description="Custom metric logged for the set (Currently only used to log floors or steps for stair machine exercises)")
    
    class Config:
        extra = "forbid"


class RoutineExerciseSet(BaseModel):
    """Single exercise set for routines (includes rep_range)."""
    index: Optional[int] = Field(None, description="Index indicating the order of the set")
    type: Optional[Literal['warmup', 'normal', 'failure', 'dropset']] = Field(None, description="The type of the set")
    weight_kg: Optional[float] = Field(None, description="Weight lifted in kilograms")
    reps: Optional[int] = Field(None, description="Number of reps logged for the set")
    rep_range: Optional[RepRange] = Field(None, description="Range of reps for the set, if applicable")
    distance_meters: Optional[float] = Field(None, description="Number of meters logged for the set")
    duration_seconds: Optional[int] = Field(None, description="Number of seconds logged for the set")
    rpe: Optional[Literal[6, 7, 7.5, 8, 8.5, 9, 9.5, 10]] = Field(None, description="RPE (Relative perceived exertion) value logged for the set")
    custom_metric: Optional[float] = Field(None, description="Custom metric logged for the set (Currently only used to log floors or steps for stair machine exercises)")
    
    class Config:
        extra = "forbid"


class WorkoutExercise(BaseModel):
    """Exercise within a workout."""
    index: Optional[int] = Field(None, description="Index indicating the order of the exercise in the workout")
    title: Optional[str] = Field(None, description="Title of the exercise")
    notes: Optional[str] = Field(None, description="Notes on the exercise")
    exercise_template_id: Optional[str] = Field(None, description="The id of the exercise template. This can be used to fetch the exercise template")
    supersets_id: Optional[int] = Field(None, description="The id of the superset that the exercise belongs to. A value of null indicates the exercise is not part of a superset")
    sets: Optional[List[ExerciseSet]] = Field(None, description="Exercise sets")
    
    class Config:
        extra = "forbid"


class Workout(BaseModel):
    """Workout model."""
    id: Optional[str] = Field(None, description="The workout ID")
    title: Optional[str] = Field(None, description="The workout title")
    description: Optional[str] = Field(None, description="The workout description")
    start_time: Optional[float] = Field(None, description="ISO 8601 timestamp of when the workout was recorded to have started")
    end_time: Optional[float] = Field(None, description="ISO 8601 timestamp of when the workout was recorded to have ended")
    updated_at: Optional[str] = Field(None, description="ISO 8601 timestamp of when the workout was last updated")
    created_at: Optional[str] = Field(None, description="ISO 8601 timestamp of when the workout was created")
    exercises: Optional[List[WorkoutExercise]] = Field(None, description="Workout exercises")
    
    class Config:
        extra = "forbid"
        validate_assignment = True


class WorkoutsResponse(HevyResponse):
    """Response model for workouts list."""
    workouts: List[Workout] = Field(..., description="List of workouts")
    page: int = Field(..., ge=1, description="Current page number")
    page_count: int = Field(..., alias="page_count", ge=1, description="Total number of pages")
    page_size: Optional[int] = Field(None, alias="pageSize", ge=1, le=100, description="Number of items per page")
    total: Optional[int] = Field(None, ge=0, description="Total number of workouts")
    
    class Config:
        extra = "forbid"


class WorkoutCountResponse(HevyResponse):
    """Response model for workout count."""
    workout_count: int = Field(..., alias="workout_count", ge=0, description="Number of workouts")
    
    class Config:
        extra = "forbid"


class UpdatedWorkout(BaseModel):
    """Updated workout event model."""
    type: str = Field(..., description="Indicates the type of the event (updated)")
    workout: Workout = Field(..., description="The updated workout")
    
    class Config:
        extra = "forbid"


class DeletedWorkout(BaseModel):
    """Deleted workout event model."""
    type: str = Field(..., description="Indicates the type of the event (deleted)")
    id: str = Field(..., description="The unique identifier of the deleted workout")
    deleted_at: Optional[str] = Field(None, description="A date string indicating when the workout was deleted")
    
    class Config:
        extra = "forbid"


# WorkoutEvent is now handled as a Union type directly in responses
WorkoutEvent = Union[UpdatedWorkout, DeletedWorkout]


class PaginatedWorkoutEvents(HevyResponse):
    """Response model for paginated workout events."""
    page: int = Field(..., description="The current page number")
    page_count: int = Field(..., description="The total number of pages available")
    events: List[WorkoutEvent] = Field(..., description="An array of workout events (either updated or deleted)")
    
    class Config:
        extra = "forbid"


class WorkoutEventsResponse(HevyResponse):
    """Response model for workout events."""
    events: List[WorkoutEvent] = Field(..., description="List of workout events")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total: Optional[int] = Field(None, ge=0, description="Total number of events")
    
    class Config:
        extra = "forbid"


# Routine-related models
class RoutineExercise(BaseModel):
    """Exercise within a routine."""
    index: Optional[int] = Field(None, description="Index indicating the order of the exercise in the routine")
    title: Optional[str] = Field(None, description="Title of the exercise")
    rest_seconds: Optional[str] = Field(None, description="The rest time in seconds between sets of the exercise")
    notes: Optional[str] = Field(None, description="Routine notes on the exercise")
    exercise_template_id: Optional[str] = Field(None, description="The id of the exercise template. This can be used to fetch the exercise template")
    supersets_id: Optional[int] = Field(None, description="The id of the superset that the exercise belongs to. A value of null indicates the exercise is not part of a superset")
    sets: Optional[List[RoutineExerciseSet]] = Field(None, description="Exercise sets")
    
    class Config:
        extra = "forbid"


class Routine(BaseModel):
    """Routine model."""
    id: Optional[str] = Field(None, description="The routine ID")
    title: Optional[str] = Field(None, description="The routine title")
    folder_id: Optional[int] = Field(None, description="The routine folder ID")
    updated_at: Optional[str] = Field(None, description="ISO 8601 timestamp of when the routine was last updated")
    created_at: Optional[str] = Field(None, description="ISO 8601 timestamp of when the routine was created")
    exercises: Optional[List[RoutineExercise]] = Field(None, description="Routine exercises")
    
    class Config:
        extra = "forbid"
        validate_assignment = True


class RoutinesResponse(HevyResponse):
    """Response model for routines list."""
    routines: List[Routine] = Field(..., description="List of routines")
    page: int = Field(..., ge=1, description="Current page number")
    page_count: int = Field(..., alias="page_count", ge=1, description="Total number of pages")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total: Optional[int] = Field(None, ge=0, description="Total number of routines")
    
    class Config:
        extra = "forbid"


class RoutineResponse(HevyResponse):
    """Response model for a single routine."""
    routine: Routine = Field(..., description="The routine data")
    
    class Config:
        extra = "forbid"


class RoutineFolder(BaseModel):
    """Routine folder model."""
    id: Optional[int] = Field(None, description="The routine folder ID")
    index: Optional[int] = Field(None, description="The routine folder index. Describes the order of the folder in the list")
    title: Optional[str] = Field(None, description="The routine folder title")
    updated_at: Optional[str] = Field(None, description="ISO 8601 timestamp of when the folder was last updated")
    created_at: Optional[str] = Field(None, description="ISO 8601 timestamp of when the folder was created")
    
    class Config:
        extra = "forbid"


class RoutineFoldersResponse(HevyResponse):
    """Response model for routine folders list."""
    routine_folders: List[RoutineFolder] = Field(..., alias="routine_folders", description="List of routine folders")
    page: int = Field(..., ge=1, description="Current page number")
    page_count: int = Field(..., alias="page_count", ge=1, description="Total number of pages")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total: Optional[int] = Field(None, ge=0, description="Total number of folders")
    
    class Config:
        extra = "forbid"


# Webhook-related models
class WebhookSubscription(BaseModel):
    """Webhook subscription model."""
    authToken: Optional[str] = Field(None, description="The auth token that will be send as Authorization header in the webhook")
    url: Optional[str] = Field(None, description="The webhook URL")
    
    class Config:
        extra = "forbid"


# Request payload models
class CreateWorkoutRequest(BaseModel):
    """Request model for creating a workout."""
    workout: Optional[Workout] = Field(None, description="Workout data")
    
    class Config:
        extra = "forbid"


class UpdateWorkoutRequest(BaseModel):
    """Request model for updating a workout."""
    workout: Workout = Field(..., description="Workout data to update")
    
    class Config:
        extra = "forbid"


class CreateRoutineRequest(BaseModel):
    """Request model for creating a routine."""
    routine: Optional[Routine] = Field(None, description="Routine data")
    
    class Config:
        extra = "forbid"


class UpdateRoutineRequest(BaseModel):
    """Request model for updating a routine."""
    routine: Routine = Field(..., description="Routine data to update")
    
    class Config:
        extra = "forbid"


class CreateRoutineFolderRequest(BaseModel):
    """Request model for creating a routine folder."""
    routine_folder: RoutineFolder = Field(..., description="Routine folder data")
    
    class Config:
        extra = "forbid"


class CreateWebhookRequest(BaseModel):
    """Request model for creating a webhook subscription."""
    url: Optional[str] = Field(None, description="The webhook URL")
    authToken: Optional[str] = Field(None, description="The auth token")
    
    class Config:
        extra = "forbid"


# Union types for API responses
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
    ErrorResponse
]


# Type aliases for common patterns
WorkoutID = str
RoutineID = str
ExerciseTemplateID = str
FolderID = int
PageNumber = int
PageSize = int
ISODateTime = str


# Additional validation helpers
class APIValidationMixin:
    """Mixin class providing common validation methods."""
    
    @staticmethod
    def validate_page_params(page: int, page_size: int) -> tuple[int, int]:
        """Validate and normalize pagination parameters."""
        if page < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")
        return page, page_size
    
    @staticmethod
    def validate_date_range(start_date: Optional[datetime], end_date: Optional[datetime]) -> tuple[Optional[datetime], Optional[datetime]]:
        """Validate date range parameters."""
        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        return start_date, end_date
