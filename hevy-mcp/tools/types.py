"""
Type definitions for Hevy API data structures using Pydantic models.
These provide clear type hints and validation for the MCP server.
Strictly adheres to the Hevy API documentation formats.
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
    id: str = Field(..., description="Exercise template ID (e.g., '05293BCA')", min_length=1)
    title: str = Field(..., description="Exercise title/name", min_length=1)
    type: Optional[str] = Field(None, description="Exercise type (e.g., 'weight_reps')")
    primary_muscle_group: Optional[str] = Field(None, description="Primary muscle group")
    secondary_muscle_groups: Optional[List[str]] = Field(None, description="Secondary muscle groups")
    is_custom: Optional[bool] = Field(None, description="Whether the exercise is custom")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
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
    """Single exercise set."""
    id: Optional[str] = Field(None, description="Set ID")
    index: Optional[int] = Field(None, description="Index indicating the order of the set")
    type: Optional[str] = Field("normal", description="The type of the set", pattern=r"^(warmup|normal|failure|dropset)$")
    weight_kg: Optional[float] = Field(None, ge=0, le=APIConstants.MAX_WEIGHT_KG, description="Weight used in kg")
    reps: Optional[int] = Field(None, ge=0, le=APIConstants.MAX_REPS, description="Number of repetitions")
    rep_range: Optional[RepRange] = Field(None, description="Range of reps for the set (Routine sets)")
    distance_meters: Optional[float] = Field(None, ge=0, le=APIConstants.MAX_DISTANCE_METERS, description="Distance covered in meters")
    duration_seconds: Optional[int] = Field(None, ge=0, le=APIConstants.MAX_DURATION_SECONDS, description="Duration in seconds")
    rpe: Optional[float] = Field(None, ge=6, le=10, description="Rating of Perceived Exertion (allowed values: 6,7,7.5,8,8.5,9,9.5,10)")
    custom_metric: Optional[float] = Field(None, description="Custom metric (used e.g. for steps/floors)")
    notes: Optional[str] = Field(None, description="Set notes")
    
    @validator('weight_kg', 'reps', 'duration_seconds', 'distance_meters', 'rpe', 'custom_metric', pre=True)
    def validate_positive_values(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be non-negative')
        return v
    
    @validator('rpe', pre=True)
    def validate_rpe(cls, v):
        if v is not None and v not in [6, 7, 7.5, 8, 8.5, 9, 9.5, 10]:
            raise ValueError('RPE must be one of: 6, 7, 7.5, 8, 8.5, 9, 9.5, 10')
        return v
    
    class Config:
        extra = "forbid"


class WorkoutExercise(BaseModel):
    """Exercise within a workout."""
    id: Optional[str] = Field(None, description="Exercise ID")
    index: Optional[int] = Field(None, description="Index indicating the order of the exercise in the workout")
    title: Optional[str] = Field(None, description="Title of the exercise")
    exercise_template_id: str = Field(..., description="Exercise template ID", min_length=1)
    superset_id: Optional[int] = Field(None, description="The id of the superset that the exercise belongs to")
    sets: List[ExerciseSet] = Field(default_factory=list, description="Exercise sets")
    notes: Optional[str] = Field(None, description="Exercise notes")
    
    class Config:
        extra = "forbid"


class Workout(BaseModel):
    """Workout model."""
    id: Optional[str] = Field(None, description="Workout ID (UUID)")
    title: Optional[str] = Field(None, description="Workout title")
    description: Optional[str] = Field(None, description="Workout description")
    start_time: Optional[datetime] = Field(None, description="ISO 8601 timestamp of when the workout was recorded to have started")
    end_time: Optional[datetime] = Field(None, description="ISO 8601 timestamp of when the workout was recorded to have ended")
    is_private: Optional[bool] = Field(None, description="Whether the workout is private")
    exercises: List[WorkoutExercise] = Field(default_factory=list, description="Workout exercises")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('id', pre=True)
    def validate_uuid(cls, v):
        if v is not None:
            try:
                uuid.UUID(str(v))
            except ValueError:
                raise ValueError('Invalid UUID format')
        return v
    
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
    deleted_at: datetime = Field(..., description="A date string indicating when the workout was deleted")
    
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
    id: Optional[str] = Field(None, description="Exercise ID")
    index: Optional[int] = Field(None, description="Index indicating the order of the exercise in the routine")
    title: Optional[str] = Field(None, description="Title of the exercise")
    exercise_template_id: str = Field(..., description="Exercise template ID", min_length=1)
    superset_id: Optional[int] = Field(None, description="The id of the superset that the exercise belongs to")
    rest_seconds: Optional[int] = Field(None, description="The rest time in seconds between sets of the exercise")
    sets: List[ExerciseSet] = Field(default_factory=list, description="Exercise sets")
    notes: Optional[str] = Field(None, description="Routine notes on the exercise")
    
    class Config:
        extra = "forbid"


class Routine(BaseModel):
    """Routine model."""
    id: Optional[str] = Field(None, description="Routine ID (UUID)")
    title: str = Field(..., description="Routine title", min_length=1)
    folder_id: Optional[int] = Field(None, description="Folder ID")
    notes: Optional[str] = Field(None, description="Routine notes")
    exercises: List[RoutineExercise] = Field(default_factory=list, description="Routine exercises")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('id', pre=True)
    def validate_uuid(cls, v):
        if v is not None:
            try:
                uuid.UUID(str(v))
            except ValueError:
                raise ValueError('Invalid UUID format')
        return v
    
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
    id: int = Field(..., description="Folder ID", ge=1)
    index: Optional[int] = Field(None, description="The routine folder index. Describes the order of the folder in the list")
    title: str = Field(..., description="Folder title", min_length=1)
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
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
    id: Optional[str] = Field(None, description="Subscription ID")
    url: str = Field(..., description="Webhook URL", pattern=r'^https?://.+')
    auth_token: str = Field(..., alias="authToken", description="Auth token for webhook", min_length=1)
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        extra = "forbid"


# Request payload models
class CreateWorkoutRequest(BaseModel):
    """Request model for creating a workout."""
    workout: Workout = Field(..., description="Workout data")
    
    class Config:
        extra = "forbid"


class UpdateWorkoutRequest(BaseModel):
    """Request model for updating a workout."""
    workout: Workout = Field(..., description="Workout data to update")
    
    class Config:
        extra = "forbid"


class CreateRoutineRequest(BaseModel):
    """Request model for creating a routine."""
    routine: Routine = Field(..., description="Routine data")
    
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
    url: str = Field(..., description="Webhook URL", pattern=r'^https?://.+')
    auth_token: str = Field(..., alias="authToken", description="Auth token", min_length=1)
    
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
