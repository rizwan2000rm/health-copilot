import axios, { AxiosInstance, AxiosResponse } from "axios";
import logger from "../utils/logger.js";
import {
  Workout,
  Exercise,
  WorkoutDetail,
  PaginatedResponse,
  WorkoutStats,
  ExerciseSearchResult,
  GetWorkoutsParams,
  GetWorkoutByIdParams,
  GetExercisesParams,
  SearchExercisesParams,
  GetWorkoutStatsParams,
} from "../types/index.js";

export class HevyApiService {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.HEVY_API_BASE_URL || "http://localhost:3000";
    const timeout = parseInt(process.env.HEVY_API_TIMEOUT || "30000");

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout,
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "Hevy-MCP-Server/1.0.0",
      },
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        logger.debug("API Request", {
          method: config.method?.toUpperCase(),
          url: config.url,
          params: config.params,
        });
        return config;
      },
      (error) => {
        logger.error("API Request Error", error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for logging and error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        logger.debug("API Response", {
          status: response.status,
          url: response.config.url,
          dataSize: JSON.stringify(response.data).length,
        });
        return response;
      },
      (error) => {
        if (error.response) {
          logger.error("API Response Error", {
            status: error.response.status,
            statusText: error.response.statusText,
            url: error.config?.url,
            data: error.response.data,
          });
        } else if (error.request) {
          logger.error("API Request Failed", {
            url: error.config?.url,
            message: error.message,
          });
        } else {
          logger.error("API Error", error);
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get paginated workouts with optional filtering
   */
  async getWorkouts(params: GetWorkoutsParams): Promise<PaginatedResponse> {
    try {
      const response = await this.client.get<PaginatedResponse>(
        "/api/workouts",
        {
          params,
        }
      );
      return response.data;
    } catch (error) {
      logger.error("Failed to get workouts", { params, error });
      throw this.handleApiError(error, "Failed to get workouts");
    }
  }

  /**
   * Get a specific workout by ID with all exercises
   */
  async getWorkoutById(params: GetWorkoutByIdParams): Promise<WorkoutDetail> {
    try {
      const response = await this.client.get<WorkoutDetail>(
        `/api/workouts/${params.id}`
      );
      return response.data;
    } catch (error) {
      logger.error("Failed to get workout by ID", { params, error });
      throw this.handleApiError(error, "Failed to get workout by ID");
    }
  }

  /**
   * Get all exercises for a specific workout
   */
  async getExercises(params: GetExercisesParams): Promise<Exercise[]> {
    try {
      const response = await this.client.get<Exercise[]>(
        `/api/workouts/${params.workout_id}/exercises`
      );
      return response.data;
    } catch (error) {
      logger.error("Failed to get exercises", { params, error });
      throw this.handleApiError(error, "Failed to get exercises");
    }
  }

  /**
   * Search exercises by title
   */
  async searchExercises(
    params: SearchExercisesParams
  ): Promise<ExerciseSearchResult> {
    try {
      const response = await this.client.get<ExerciseSearchResult>(
        "/api/exercises/search",
        {
          params: {
            query: params.query,
            limit: params.limit,
          },
        }
      );
      return response.data;
    } catch (error) {
      logger.error("Failed to search exercises", { params, error });
      throw this.handleApiError(error, "Failed to search exercises");
    }
  }

  /**
   * Get workout statistics and analytics
   */
  async getWorkoutStats(params: GetWorkoutStatsParams): Promise<WorkoutStats> {
    try {
      const response = await this.client.get<WorkoutStats>(
        "/api/workouts/stats",
        {
          params,
        }
      );
      return response.data;
    } catch (error) {
      logger.error("Failed to get workout stats", { params, error });
      throw this.handleApiError(error, "Failed to get workout stats");
    }
  }

  /**
   * Health check for the API
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      const response = await this.client.get("/health");
      return response.data;
    } catch (error) {
      logger.error("Health check failed", { error });
      throw this.handleApiError(error, "Health check failed");
    }
  }

  /**
   * Handle API errors and create consistent error format
   */
  private handleApiError(error: any, defaultMessage: string): Error {
    if (error.response?.data?.message) {
      return new Error(error.response.data.message);
    }
    if (error.message) {
      return new Error(error.message);
    }
    return new Error(defaultMessage);
  }

  /**
   * Test the API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      logger.error("API connection test failed", { error });
      return false;
    }
  }
}

export default HevyApiService;
