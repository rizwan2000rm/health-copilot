import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import logger from "../utils/logger.js";
import HevyApiService from "../services/hevyApi.js";
import {
  GetWorkoutsParamsSchema,
  GetWorkoutByIdParamsSchema,
  GetExercisesParamsSchema,
  SearchExercisesParamsSchema,
  GetWorkoutStatsParamsSchema,
} from "../types/index.js";

// Initialize the Hevy API service
const hevyApi = new HevyApiService();

// Create MCP server
const server = new Server({
  name: process.env.MCP_SERVER_NAME || "hevy-mcp-server",
  version: process.env.MCP_SERVER_VERSION || "1.0.0",
});

// Tool: Get Workouts
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_workouts",
        description:
          "Retrieve a paginated list of workouts with optional filtering by search terms, start date, and end date",
        inputSchema: {
          type: "object",
          properties: {
            page: {
              type: "number",
              description: "Page number for pagination (default: 1)",
              minimum: 1,
            },
            limit: {
              type: "number",
              description:
                "Number of workouts per page (default: 20, max: 100)",
              minimum: 1,
              maximum: 100,
            },
            search: {
              type: "string",
              description:
                "Search term to filter workouts by title or description",
            },
            start_date: {
              type: "string",
              description: "Start date filter (ISO format: YYYY-MM-DD)",
            },
            end_date: {
              type: "string",
              description: "End date filter (ISO format: YYYY-MM-DD)",
            },
          },
        },
      },
      {
        name: "get_workout_by_id",
        description: "Retrieve a specific workout by ID with all its exercises",
        inputSchema: {
          type: "object",
          properties: {
            id: {
              type: "number",
              description: "The unique identifier of the workout",
            },
          },
          required: ["id"],
        },
      },
      {
        name: "get_exercises",
        description: "Retrieve all exercises for a specific workout",
        inputSchema: {
          type: "object",
          properties: {
            workout_id: {
              type: "number",
              description: "The ID of the workout to get exercises for",
            },
          },
          required: ["workout_id"],
        },
      },
      {
        name: "search_exercises",
        description: "Search for exercises by title across all workouts",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query for exercise titles",
            },
            limit: {
              type: "number",
              description:
                "Maximum number of results to return (default: 20, max: 100)",
              minimum: 1,
              maximum: 100,
            },
          },
          required: ["query"],
        },
      },
      {
        name: "get_workout_stats",
        description: "Retrieve comprehensive workout statistics and analytics",
        inputSchema: {
          type: "object",
          properties: {
            start_date: {
              type: "string",
              description: "Start date for statistics (ISO format: YYYY-MM-DD)",
            },
            end_date: {
              type: "string",
              description: "End date for statistics (ISO format: YYYY-MM-DD)",
            },
          },
        },
      },
      {
        name: "health_check",
        description: "Check the health status of the Hevy API",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ],
  };
});

// Tool: Get Workouts Implementation
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    logger.info("Tool called", { name, arguments: args });

    switch (name) {
      case "get_workouts": {
        const validatedArgs = GetWorkoutsParamsSchema.parse(args);
        const result = await hevyApi.getWorkouts(validatedArgs);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "get_workout_by_id": {
        const validatedArgs = GetWorkoutByIdParamsSchema.parse(args);
        const result = await hevyApi.getWorkoutById(validatedArgs);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "get_exercises": {
        const validatedArgs = GetExercisesParamsSchema.parse(args);
        const result = await hevyApi.getExercises(validatedArgs);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "search_exercises": {
        const validatedArgs = SearchExercisesParamsSchema.parse(args);
        const result = await hevyApi.searchExercises(validatedArgs);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "get_workout_stats": {
        const validatedArgs = GetWorkoutStatsParamsSchema.parse(args);
        const result = await hevyApi.getWorkoutStats(validatedArgs);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "health_check": {
        const result = await hevyApi.healthCheck();
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    logger.error("Tool execution failed", { name, arguments: args, error });

    const errorMessage =
      error instanceof Error ? error.message : "Unknown error occurred";
    return {
      content: [
        {
          type: "text",
          text: `Error executing tool '${name}': ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  try {
    logger.info("Starting Hevy MCP Server...");

    // Test API connection
    const isConnected = await hevyApi.testConnection();
    if (!isConnected) {
      logger.warn("Hevy API connection test failed, but continuing...");
    } else {
      logger.info("Hevy API connection test successful");
    }

    // Start the server with stdio transport
    const transport = new StdioServerTransport();
    await server.connect(transport);

    logger.info("Hevy MCP Server started successfully");

    // Handle graceful shutdown
    process.on("SIGINT", async () => {
      logger.info("Received SIGINT, shutting down gracefully...");
      await server.close();
      process.exit(0);
    });

    process.on("SIGTERM", async () => {
      logger.info("Received SIGTERM, shutting down gracefully...");
      await server.close();
      process.exit(0);
    });
  } catch (error) {
    logger.error("Failed to start MCP server", error);
    process.exit(1);
  }
}

// Run the server
main().catch((error) => {
  logger.error("Unhandled error in main", error);
  process.exit(1);
});
