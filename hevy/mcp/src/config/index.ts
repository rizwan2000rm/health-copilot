import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// Load environment variables
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, "../../env.example") });

export interface Config {
  server: {
    name: string;
    version: string;
    port: number;
    host: string;
  };
  hevy: {
    baseUrl: string;
    timeout: number;
  };
  logging: {
    level: string;
    filePath: string;
    maxSize: number;
    maxFiles: number;
  };
  security: {
    cors: {
      origin: string[];
      credentials: boolean;
    };
    rateLimit: {
      windowMs: number;
      maxRequests: number;
    };
  };
}

export const config: Config = {
  server: {
    name: process.env.MCP_SERVER_NAME || "hevy-mcp-server",
    version: process.env.MCP_SERVER_VERSION || "1.0.0",
    port: parseInt(process.env.PORT || "3001"),
    host: process.env.HOST || "localhost",
  },
  hevy: {
    baseUrl: process.env.HEVY_API_BASE_URL || "http://localhost:3000/api",
    timeout: parseInt(process.env.HEVY_API_TIMEOUT || "30000"),
  },
  logging: {
    level: process.env.LOG_LEVEL || "info",
    filePath: process.env.LOG_FILE_PATH || "./logs/mcp-server.log",
    maxSize: 10 * 1024 * 1024, // 10MB
    maxFiles: 5,
  },
  security: {
    cors: {
      origin: process.env.CORS_ORIGIN?.split(",") || ["http://localhost:3000"],
      credentials: true,
    },
    rateLimit: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      maxRequests: 100, // limit each IP to 100 requests per windowMs
    },
  },
};

// Validation function to ensure all required config values are present
export function validateConfig(): void {
  const requiredFields = [
    "server.name",
    "server.version",
    "hevy.baseUrl",
    "logging.level",
  ];

  for (const field of requiredFields) {
    const keys = field.split(".");
    let value: any = config;
    for (const key of keys) {
      value = value?.[key];
    }
    if (!value) {
      throw new Error(`Missing required configuration: ${field}`);
    }
  }

  // Validate URL format
  try {
    new URL(config.hevy.baseUrl);
  } catch (error) {
    throw new Error(`Invalid Hevy API base URL: ${config.hevy.baseUrl}`);
  }

  // Validate port range
  if (config.server.port < 1 || config.server.port > 65535) {
    throw new Error(`Invalid port number: ${config.server.port}`);
  }

  // Validate timeout
  if (config.hevy.timeout < 1000 || config.hevy.timeout > 300000) {
    throw new Error(`Invalid timeout value: ${config.hevy.timeout}`);
  }
}

// Export default config
export default config;
