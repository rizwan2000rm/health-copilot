import logger from './logger.js';

export enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  API_ERROR = 'API_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

export interface AppError extends Error {
  code: ErrorCode;
  statusCode: number;
  isOperational: boolean;
  details?: Record<string, any>;
}

export class ValidationError extends Error implements AppError {
  public readonly code = ErrorCode.VALIDATION_ERROR;
  public readonly statusCode = 400;
  public readonly isOperational = true;
  public readonly details?: Record<string, any>;

  constructor(message: string, details?: Record<string, any>) {
    super(message);
    this.name = 'ValidationError';
    this.details = details;
  }
}

export class ApiError extends Error implements AppError {
  public readonly code = ErrorCode.API_ERROR;
  public readonly statusCode: number;
  public readonly isOperational = true;
  public readonly details?: Record<string, any>;

  constructor(message: string, statusCode: number = 500, details?: Record<string, any>) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

export class NetworkError extends Error implements AppError {
  public readonly code = ErrorCode.NETWORK_ERROR;
  public readonly statusCode = 503;
  public readonly isOperational = true;
  public readonly details?: Record<string, any>;

  constructor(message: string, details?: Record<string, any>) {
    super(message);
    this.name = 'NetworkError';
    this.details = details;
  }
}

export class InternalError extends Error implements AppError {
  public readonly code = ErrorCode.INTERNAL_ERROR;
  public readonly statusCode = 500;
  public readonly isOperational = false;
  public readonly details?: Record<string, any>;

  constructor(message: string, details?: Record<string, any>) {
    super(message);
    this.name = 'InternalError';
    this.details = details;
  }
}

/**
 * Create an appropriate error based on the input
 */
export function createError(
  error: unknown,
  context: string,
  fallbackMessage: string = 'An unexpected error occurred'
): AppError {
  // If it's already an AppError, return it
  if (isAppError(error)) {
    return error;
  }

  // Handle axios errors
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosError = error as any;
    if (axiosError.response) {
      // Server responded with error status
      return new ApiError(
        axiosError.response.data?.message || axiosError.message,
        axiosError.response.status,
        {
          url: axiosError.config?.url,
          method: axiosError.config?.method,
          status: axiosError.response.status,
          data: axiosError.response.data,
        }
      );
    } else if (axiosError.request) {
      // Request was made but no response received
      return new NetworkError(
        'No response received from server',
        {
          url: axiosError.config?.url,
          method: axiosError.config?.method,
          timeout: axiosError.config?.timeout,
        }
      );
    } else {
      // Something else happened
      return new NetworkError(
        axiosError.message || 'Network request failed',
        {
          url: axiosError.config?.url,
          method: axiosError.config?.method,
        }
      );
    }
  }

  // Handle validation errors
  if (error && typeof error === 'object' && 'name' in error && error.name === 'ZodError') {
    const zodError = error as any;
    return new ValidationError(
      'Input validation failed',
      {
        errors: zodError.errors,
        context,
      }
    );
  }

  // Handle generic errors
  if (error instanceof Error) {
    return new InternalError(
      error.message || fallbackMessage,
      {
        name: error.name,
        stack: error.stack,
        context,
      }
    );
  }

  // Handle unknown errors
  return new InternalError(
    fallbackMessage,
    {
      originalError: error,
      context,
    }
  );
}

/**
 * Type guard to check if an error is an AppError
 */
export function isAppError(error: unknown): error is AppError {
  return (
    error instanceof Error &&
    'code' in error &&
    'statusCode' in error &&
    'isOperational' in error
  );
}

/**
 * Log error with appropriate level based on error type
 */
export function logError(error: AppError, context: string): void {
  const logData = {
    code: error.code,
    statusCode: error.statusCode,
    message: error.message,
    context,
    details: error.details,
    stack: error.stack,
  };

  if (error.isOperational) {
    logger.warn('Operational error occurred', logData);
  } else {
    logger.error('System error occurred', logData);
  }
}

/**
 * Format error for MCP response
 */
export function formatErrorForMCP(error: AppError): string {
  const baseMessage = `Error (${error.code}): ${error.message}`;
  
  if (error.details && Object.keys(error.details).length > 0) {
    return `${baseMessage}\n\nDetails: ${JSON.stringify(error.details, null, 2)}`;
  }
  
  return baseMessage;
}

/**
 * Handle errors gracefully and return appropriate MCP response
 */
export function handleErrorForMCP(
  error: unknown,
  context: string,
  toolName: string
): { content: Array<{ type: string; text: string }>; isError: boolean } {
  const appError = createError(error, context);
  logError(appError, context);

  return {
    content: [
      {
        type: 'text',
        text: formatErrorForMCP(appError),
      },
    ],
    isError: true,
  };
}
