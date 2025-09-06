"""
Type definitions for Hevy API data structures using Pydantic models.
These provide clear type hints and validation for the MCP server.
"""

from typing import Any, Optional, List, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime


# Base response models
class HevyResponse(BaseModel):
    """Base response model for Hevy API responses."""
    pass


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: Optional[str] = None


# Exercise-related models
class ExerciseTemplate(BaseModel):
    """Exercise template model."""
    id: str = Field(..., description="Exercise template ID (e.g., '05293BCA')")
    name: str = Field(..., description="Exercise name")
    category: Optional[str] = Field(None, description="Exercise category")
    muscle_groups: Optional[List[str]] = Field(None, description="Target muscle groups")
    equipment: Optional[str] = Field(None, description="Required equipment")
    instructions: Optional[str] = Field(None, description="Exercise instructions")
    tips: Optional[str] = Field(None, description="Exercise tips")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ExerciseTemplatesResponse(HevyResponse):
    """Response model for exercise templates list."""
    templates: List[ExerciseTemplate]
    page: int
    page_size: int
    total: Optional[int] = None


class ExerciseHistoryEntry(BaseModel):
    """Single exercise history entry."""
    id: str = Field(..., description="History entry ID")
    exercise_template_id: str = Field(..., description="Exercise template ID")
    workout_id: str = Field(..., description="Workout ID")
    date: datetime = Field(..., description="Exercise date")
    weight: Optional[float] = Field(None, description="Weight used")
    reps: Optional[int] = Field(None, description="Number of repetitions")
    sets: Optional[int] = Field(None, description="Number of sets")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    distance: Optional[float] = Field(None, description="Distance covered")
    notes: Optional[str] = Field(None, description="Exercise notes")


class ExerciseHistoryResponse(HevyResponse):
    """Response model for exercise history."""
    history: List[ExerciseHistoryEntry]
    exercise_template_id: str
    total: Optional[int] = None


# Workout-related models
class ExerciseSet(BaseModel):
    """Single exercise set."""
    id: Optional[str] = Field(None, description="Set ID")
    weight: Optional[float] = Field(None, description="Weight used")
    reps: Optional[int] = Field(None, description="Number of repetitions")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    distance: Optional[float] = Field(None, description="Distance covered")
    rest_time: Optional[int] = Field(None, description="Rest time in seconds")
    notes: Optional[str] = Field(None, description="Set notes")


class WorkoutExercise(BaseModel):
    """Exercise within a workout."""
    id: Optional[str] = Field(None, description="Exercise ID")
    exercise_template_id: str = Field(..., description="Exercise template ID")
    exercise_name: Optional[str] = Field(None, description="Exercise name")
    order: Optional[int] = Field(None, description="Exercise order in workout")
    sets: List[ExerciseSet] = Field(default_factory=list, description="Exercise sets")
    notes: Optional[str] = Field(None, description="Exercise notes")


class Workout(BaseModel):
    """Workout model."""
    id: Optional[str] = Field(None, description="Workout ID (UUID)")
    name: str = Field(..., description="Workout name")
    date: Optional[datetime] = Field(None, description="Workout date")
    notes: Optional[str] = Field(None, description="Workout notes")
    exercises: List[WorkoutExercise] = Field(default_factory=list, description="Workout exercises")
    duration: Optional[int] = Field(None, description="Total workout duration in seconds")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class WorkoutsResponse(HevyResponse):
    """Response model for workouts list."""
    workouts: List[Workout]
    page: int
    page_size: int
    total: Optional[int] = None


class WorkoutCountResponse(HevyResponse):
    """Response model for workout count."""
    count: int


class WorkoutEvent(BaseModel):
    """Workout event model."""
    id: str = Field(..., description="Event ID")
    workout_id: str = Field(..., description="Workout ID")
    event_type: str = Field(..., description="Event type (e.g., 'created', 'updated')")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Optional[dict[str, Any]] = Field(None, description="Event data")


class WorkoutEventsResponse(HevyResponse):
    """Response model for workout events."""
    events: List[WorkoutEvent]
    page: int
    page_size: int
    total: Optional[int] = None


# Routine-related models
class RoutineExercise(BaseModel):
    """Exercise within a routine."""
    id: Optional[str] = Field(None, description="Exercise ID")
    exercise_template_id: str = Field(..., description="Exercise template ID")
    exercise_name: Optional[str] = Field(None, description="Exercise name")
    order: Optional[int] = Field(None, description="Exercise order in routine")
    sets: List[ExerciseSet] = Field(default_factory=list, description="Exercise sets")
    notes: Optional[str] = Field(None, description="Exercise notes")


class Routine(BaseModel):
    """Routine model."""
    id: Optional[str] = Field(None, description="Routine ID (UUID)")
    title: str = Field(..., description="Routine title")
    folder_id: Optional[int] = Field(None, description="Folder ID")
    notes: Optional[str] = Field(None, description="Routine notes")
    exercises: List[RoutineExercise] = Field(default_factory=list, description="Routine exercises")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class RoutinesResponse(HevyResponse):
    """Response model for routines list."""
    routines: List[Routine]
    page: int
    page_size: int
    total: Optional[int] = None


class RoutineFolder(BaseModel):
    """Routine folder model."""
    id: int = Field(..., description="Folder ID")
    title: str = Field(..., description="Folder title")
    order: Optional[int] = Field(None, description="Folder order")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class RoutineFoldersResponse(HevyResponse):
    """Response model for routine folders list."""
    folders: List[RoutineFolder]
    page: int
    page_size: int
    total: Optional[int] = None


# Webhook-related models
class WebhookSubscription(BaseModel):
    """Webhook subscription model."""
    id: Optional[str] = Field(None, description="Subscription ID")
    url: str = Field(..., description="Webhook URL")
    auth_token: str = Field(..., alias="authToken", description="Auth token for webhook")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


# Request payload models
class CreateWorkoutRequest(BaseModel):
    """Request model for creating a workout."""
    workout: Workout = Field(..., description="Workout data")


class UpdateWorkoutRequest(BaseModel):
    """Request model for updating a workout."""
    workout: Workout = Field(..., description="Workout data to update")


class CreateRoutineRequest(BaseModel):
    """Request model for creating a routine."""
    routine: Routine = Field(..., description="Routine data")


class UpdateRoutineRequest(BaseModel):
    """Request model for updating a routine."""
    routine: Routine = Field(..., description="Routine data to update")


class CreateRoutineFolderRequest(BaseModel):
    """Request model for creating a routine folder."""
    routine_folder: RoutineFolder = Field(..., description="Routine folder data")


class CreateWebhookRequest(BaseModel):
    """Request model for creating a webhook subscription."""
    url: str = Field(..., description="Webhook URL")
    auth_token: str = Field(..., alias="authToken", description="Auth token")


# Union types for API responses
HevyAPIResponse = Union[
    ExerciseTemplatesResponse,
    ExerciseTemplate,
    ExerciseHistoryResponse,
    WorkoutsResponse,
    Workout,
    WorkoutCountResponse,
    WorkoutEventsResponse,
    RoutinesResponse,
    Routine,
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
