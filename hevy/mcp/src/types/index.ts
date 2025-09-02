import { z } from 'zod';

// Hevy API Response Schemas
export const WorkoutSchema = z.object({
  id: z.number(),
  title: z.string(),
  start_time: z.string(),
  end_time: z.string(),
  description: z.string().nullable(),
  created_at: z.string(),
  exercise_count: z.number(),
  total_duration: z.number().nullable(),
});

export const ExerciseSchema = z.object({
  id: z.number(),
  workout_id: z.number(),
  exercise_title: z.string(),
  superset_id: z.string().nullable(),
  exercise_notes: z.string().nullable(),
  set_index: z.number(),
  set_type: z.string(),
  weight_kg: z.number().nullable(),
  reps: z.number().nullable(),
  distance_km: z.number().nullable(),
  duration_seconds: z.number().nullable(),
  rpe: z.number().nullable(),
});

export const WorkoutDetailSchema = z.object({
  workout: WorkoutSchema,
  exercises: z.array(ExerciseSchema),
});

export const PaginatedResponseSchema = z.object({
  data: z.array(WorkoutSchema),
  pagination: z.object({
    page: z.number(),
    limit: z.number(),
    total: z.number(),
    total_pages: z.number(),
  }),
});

// MCP Tool Schemas
export const GetWorkoutsParamsSchema = z.object({
  page: z.number().min(1).default(1),
  limit: z.number().min(1).max(100).default(20),
  search: z.string().optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
});

export const GetWorkoutByIdParamsSchema = z.object({
  id: z.number().positive(),
});

export const GetExercisesParamsSchema = z.object({
  workout_id: z.number().positive(),
});

export const SearchExercisesParamsSchema = z.object({
  query: z.string().min(1),
  limit: z.number().min(1).max(100).default(20),
});

export const GetWorkoutStatsParamsSchema = z.object({
  start_date: z.string().optional(),
  end_date: z.string().optional(),
});

// Type exports
export type Workout = z.infer<typeof WorkoutSchema>;
export type Exercise = z.infer<typeof ExerciseSchema>;
export type WorkoutDetail = z.infer<typeof WorkoutDetailSchema>;
export type PaginatedResponse = z.infer<typeof PaginatedResponseSchema>;
export type GetWorkoutsParams = z.infer<typeof GetWorkoutsParamsSchema>;
export type GetWorkoutByIdParams = z.infer<typeof GetWorkoutByIdParamsSchema>;
export type GetExercisesParams = z.infer<typeof GetExercisesParamsSchema>;
export type SearchExercisesParams = z.infer<typeof SearchExercisesParamsSchema>;
export type GetWorkoutStatsParams = z.infer<typeof GetWorkoutStatsParamsSchema>;

// MCP Tool Result Types
export interface WorkoutStats {
  total_workouts: number;
  total_exercises: number;
  total_duration: number;
  average_workout_duration: number;
  most_common_exercises: Array<{
    exercise_title: string;
    count: number;
  }>;
  workout_frequency: Array<{
    date: string;
    count: number;
  }>;
}

export interface ExerciseSearchResult {
  exercises: Exercise[];
  total: number;
}

export interface ApiError {
  error: string;
  message: string;
  statusCode: number;
  timestamp: string;
}
