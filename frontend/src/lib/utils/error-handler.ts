// frontend/src/lib/utils/error-handler.ts

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

export class ErrorHandler {
  static handle(error: any, context?: string): ApiError {
    let message = 'An unexpected error occurred';
    let status: number | undefined;
    let details: any;

    if (error instanceof Error) {
      // Handle standard Error objects
      message = error.message;

      // Check if it's a fetch error
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        message = 'Network error. Please check your connection and try again.';
      }
    } else if (typeof error === 'object' && error !== null) {
      // Handle API response errors
      if (error.status) {
        status = error.status;
        message = this.getMessageFromStatus(error.status);
      }

      // Handle API response body
      if (error.detail) {
        message = typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail);
      } else if (error.message) {
        message = error.message;
      }

      details = error;
    } else if (typeof error === 'string') {
      message = error;
    }

    // Add context to message if provided
    if (context) {
      message = `${context}: ${message}`;
    }

    return { message, status, details };
  }

  private static getMessageFromStatus(status: number): string {
    switch (status) {
      case 400:
        return 'Bad request. Please check your input and try again.';
      case 401:
        return 'Unauthorized. Please log in to continue.';
      case 403:
        return 'Forbidden. You do not have permission to perform this action.';
      case 404:
        return 'Resource not found.';
      case 409:
        return 'Conflict. The resource already exists.';
      case 422:
        return 'Unprocessable entity. Please check your input and try again.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Internal server error. Please try again later.';
      case 502:
        return 'Bad gateway. Please try again later.';
      case 503:
        return 'Service unavailable. Please try again later.';
      default:
        return `Error ${status}. Please try again.`;
    }
  }

  static logError(error: any, context?: string): void {
    const handledError = this.handle(error, context);
    console.error('Error:', handledError);

    // In a real app, you might send this to an error tracking service
    // Example: send to Sentry, LogRocket, etc.
  }

  static isNetworkError(error: any): boolean {
    if (error instanceof Error) {
      return error.name === 'TypeError' && error.message.includes('fetch');
    }
    return false;
  }

  static isAuthError(error: any): boolean {
    if (typeof error === 'object' && error.status) {
      return error.status === 401;
    }
    return false;
  }
}