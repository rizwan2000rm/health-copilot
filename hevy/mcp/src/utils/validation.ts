import { z } from 'zod';
import logger from './logger.js';

/**
 * Validate and sanitize input parameters
 */
export function validateAndSanitize<T>(
  schema: z.ZodSchema<T>,
  input: unknown,
  context: string
): T {
  try {
    const result = schema.parse(input);
    logger.debug('Input validation successful', { context, input: result });
    return result;
  } catch (error) {
    if (error instanceof z.ZodError) {
      const validationErrors = error.errors.map(err => ({
        field: err.path.join('.'),
        message: err.message,
        code: err.code,
      }));
      
      logger.warn('Input validation failed', {
        context,
        input,
        errors: validationErrors,
      });
      
      throw new Error(
        `Validation failed for ${context}: ${validationErrors
          .map(err => `${err.field}: ${err.message}`)
          .join(', ')}`
      );
    }
    
    logger.error('Unexpected validation error', { context, input, error });
    throw new Error(`Unexpected validation error for ${context}`);
  }
}

/**
 * Safe JSON parsing with error handling
 */
export function safeJsonParse<T>(jsonString: string, fallback: T): T {
  try {
    return JSON.parse(jsonString) as T;
  } catch (error) {
    logger.warn('JSON parsing failed, using fallback', {
      jsonString,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return fallback;
  }
}

/**
 * Validate date strings
 */
export function validateDateString(dateString: string, fieldName: string): string {
  const date = new Date(dateString);
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid date format for ${fieldName}: ${dateString}`);
  }
  return dateString;
}

/**
 * Validate numeric ranges
 */
export function validateNumericRange(
  value: number,
  min: number,
  max: number,
  fieldName: string
): number {
  if (value < min || value > max) {
    throw new Error(
      `${fieldName} must be between ${min} and ${max}, got ${value}`
    );
  }
  return value;
}

/**
 * Sanitize string inputs
 */
export function sanitizeString(input: string, maxLength: number = 1000): string {
  if (typeof input !== 'string') {
    throw new Error('Input must be a string');
  }
  
  // Remove null bytes and control characters
  let sanitized = input
    .replace(/\0/g, '')
    .replace(/[\x00-\x1F\x7F-\x9F]/g, '')
    .trim();
  
  // Limit length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
    logger.warn('String truncated due to length limit', {
      originalLength: input.length,
      maxLength,
      field: 'input',
    });
  }
  
  return sanitized;
}

/**
 * Validate pagination parameters
 */
export function validatePaginationParams(
  page: number,
  limit: number,
  maxLimit: number = 100
): { page: number; limit: number } {
  const validatedPage = Math.max(1, Math.floor(page) || 1);
  const validatedLimit = Math.min(
    maxLimit,
    Math.max(1, Math.floor(limit) || 20)
  );
  
  return {
    page: validatedPage,
    limit: validatedLimit,
  };
}
