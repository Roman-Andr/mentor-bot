import { logger } from "./logger";

export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number,
    public context?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "AppError";
  }
}

export function handleError(error: unknown, context?: Record<string, unknown>): AppError {
  // Already an AppError
  if (error instanceof AppError) {
    logger.error(error.message, { code: error.code, statusCode: error.statusCode, context: { ...error.context, ...context } });
    return error;
  }

  // API Error with message
  if (error && typeof error === "object" && "message" in error) {
    const appError = new AppError(String(error.message), "API_ERROR", undefined, context);
    logger.error(appError.message, { error, context });
    return appError;
  }

  // Generic Error
  if (error instanceof Error) {
    const appError = new AppError(error.message, "GENERIC_ERROR", undefined, context);
    logger.error(appError.message, { error, context });
    return appError;
  }

  // Unknown error type
  const appError = new AppError("An unknown error occurred", "UNKNOWN_ERROR", undefined, context);
  logger.error(appError.message, { error, context });
  return appError;
}

export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}
