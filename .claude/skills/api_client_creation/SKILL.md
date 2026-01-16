# API Client Creation Skill

## Description
Create centralized API client class with private request method using generics, automatic JWT token injection, proper error handling, typed methods for all endpoints, and environment variable configuration.

## When to Use
- Setting up API communication layer for frontend
- Creating type-safe API calls to backend
- Implementing centralized authentication token management
- Adding global error handling for API requests
- Configuring API endpoints with environment variables

## Prerequisites
- Next.js 15+ with App Router configured
- TypeScript enabled
- Better Auth configured (or authentication system in place)
- Backend API endpoints available
- Environment variables configured

## Core Concepts

### Centralized API Client
- Single source of truth for all API calls
- Automatic JWT token injection
- Type-safe methods for all endpoints
- Global error handling
- Request/response interceptors
- Consistent error messages

### Type Safety with Generics
- Generic request method for reusability
- Typed request/response interfaces
- Type inference for API responses
- Compile-time error checking

## Skill Steps

### 1. Create Type Definitions

**API Types** (`types/api.ts`):

```typescript
// Task types
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'low';
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  tag_ids?: number[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: 'high' | 'medium' | 'low';
  completed?: boolean;
  tag_ids?: number[];
}

// Tag types
export interface Tag {
  id: number;
  user_id: string;
  name: string;
  created_at: string;
}

export interface TagCreate {
  name: string;
}

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface SignUpData {
  email: string;
  password: string;
  name: string;
}

export interface SignInData {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// API Error types
export interface APIError {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, any>;
}

// Query parameters
export interface TaskQueryParams {
  status?: 'all' | 'pending' | 'completed';
  priority?: string; // Comma-separated: "high,medium"
  tags?: string; // Comma-separated tag IDs: "1,2,3"
  search?: string;
  sort_by?: 'created_at' | 'priority' | 'title';
  sort_order?: 'asc' | 'desc';
}

export interface TagAutocompleteParams {
  query: string;
  limit?: number;
}
```

### 2. Create Custom API Error Class

**API Error** (`lib/api/errors.ts`):

```typescript
export class APIError extends Error {
  public status: number;
  public code?: string;
  public details?: Record<string, any>;

  constructor(
    message: string,
    status: number,
    code?: string,
    details?: Record<string, any>
  ) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
    this.details = details;

    // Maintains proper stack trace for where error was thrown (V8 only)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, APIError);
    }
  }

  public isUnauthorized(): boolean {
    return this.status === 401;
  }

  public isForbidden(): boolean {
    return this.status === 403;
  }

  public isNotFound(): boolean {
    return this.status === 404;
  }

  public isValidationError(): boolean {
    return this.status === 400 || this.status === 422;
  }

  public isServerError(): boolean {
    return this.status >= 500;
  }
}
```

### 3. Create Core API Client Class

**API Client** (`lib/api/client.ts`):

```typescript
import { APIError } from './errors';
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskQueryParams,
  Tag,
  TagCreate,
  TagAutocompleteParams,
  AuthResponse,
  SignUpData,
  SignInData,
} from '@/types/api';

class APIClient {
  private baseURL: string;
  private getToken: () => Promise<string | null>;

  constructor(baseURL: string, getToken: () => Promise<string | null>) {
    this.baseURL = baseURL;
    this.getToken = getToken;
  }

  /**
   * Private generic request method with automatic token injection
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Get authentication token
    const token = await this.getToken();

    // Prepare headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle non-OK responses
      if (!response.ok) {
        await this.handleErrorResponse(response);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      // Parse JSON response
      const data = await response.json();
      return data as T;
    } catch (error) {
      // Re-throw APIError as-is
      if (error instanceof APIError) {
        throw error;
      }

      // Handle network errors
      if (error instanceof TypeError) {
        throw new APIError(
          'Network error: Unable to connect to the server',
          0,
          'NETWORK_ERROR'
        );
      }

      // Handle unexpected errors
      throw new APIError(
        error instanceof Error ? error.message : 'An unexpected error occurred',
        0,
        'UNKNOWN_ERROR'
      );
    }
  }

  /**
   * Handle error responses and throw APIError
   */
  private async handleErrorResponse(response: Response): Promise<never> {
    let errorMessage = 'An error occurred';
    let errorCode: string | undefined;
    let errorDetails: Record<string, any> | undefined;

    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.detail || errorMessage;
      errorCode = errorData.code;
      errorDetails = errorData.details || errorData.errors;
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }

    throw new APIError(errorMessage, response.status, errorCode, errorDetails);
  }

  /**
   * Build query string from parameters
   */
  private buildQueryString(params: Record<string, any>): string {
    const searchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    return queryString ? `?${queryString}` : '';
  }

  // ==================== Authentication Methods ====================

  /**
   * Sign up a new user
   */
  async signUp(data: SignUpData): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Sign in an existing user
   */
  async signIn(data: SignInData): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/signin', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ==================== Task Methods ====================

  /**
   * Get all tasks for a user with optional filters
   */
  async getTasks(userId: string, params?: TaskQueryParams): Promise<Task[]> {
    const queryString = params ? this.buildQueryString(params) : '';
    return this.request<Task[]>(`/api/${userId}/tasks${queryString}`);
  }

  /**
   * Get a single task by ID
   */
  async getTask(userId: string, taskId: number): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`);
  }

  /**
   * Create a new task
   */
  async createTask(userId: string, data: TaskCreate): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Update an existing task
   */
  async updateTask(
    userId: string,
    taskId: number,
    data: TaskUpdate
  ): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Delete a task
   */
  async deleteTask(userId: string, taskId: number): Promise<void> {
    return this.request<void>(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Toggle task completion status
   */
  async toggleTaskComplete(userId: string, taskId: number): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }

  // ==================== Tag Methods ====================

  /**
   * Get all tags for a user
   */
  async getTags(userId: string): Promise<Tag[]> {
    return this.request<Tag[]>(`/api/${userId}/tags`);
  }

  /**
   * Create a new tag
   */
  async createTag(userId: string, data: TagCreate): Promise<Tag> {
    return this.request<Tag>(`/api/${userId}/tags`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get tag autocomplete suggestions
   */
  async getTagAutocomplete(
    userId: string,
    params: TagAutocompleteParams
  ): Promise<Tag[]> {
    const queryString = this.buildQueryString(params);
    return this.request<Tag[]>(`/api/${userId}/tags/autocomplete${queryString}`);
  }

  /**
   * Delete a tag
   */
  async deleteTag(userId: string, tagId: number): Promise<void> {
    return this.request<void>(`/api/${userId}/tags/${tagId}`, {
      method: 'DELETE',
    });
  }
}

// ==================== API Client Instance ====================

/**
 * Get authentication token from Better Auth session
 */
async function getAuthToken(): Promise<string | null> {
  // This implementation depends on your auth setup
  // For Better Auth with JWT:
  try {
    // Option 1: Get from Better Auth session (server-side)
    // const session = await auth.api.getSession({ headers: await headers() });
    // return session?.session.token || null;

    // Option 2: Get from client-side storage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      return token;
    }

    return null;
  } catch {
    return null;
  }
}

/**
 * Singleton API client instance
 */
export const apiClient = new APIClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  getAuthToken
);

// Export types for consumers
export type { APIClient };
export { APIError };
```

### 4. Environment Variable Configuration

**.env.local**:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**.env.example**:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

### 5. Usage in Server Components

**Server Component** (`app/(dashboard)/tasks/page.tsx`):

```typescript
import { apiClient } from '@/lib/api/client';
import { TaskList } from '@/components/tasks/TaskList';
import { getServerSession } from '@/lib/auth/server';
import { redirect } from 'next/navigation';

export default async function TasksPage({
  searchParams,
}: {
  searchParams: { status?: string; priority?: string };
}) {
  const session = await getServerSession();
  if (!session) redirect('/signin');

  try {
    const tasks = await apiClient.getTasks(session.userId, {
      status: searchParams.status as 'all' | 'pending' | 'completed',
      priority: searchParams.priority,
    });

    return <TaskList initialTasks={tasks} userId={session.userId} />;
  } catch (error) {
    if (error instanceof APIError && error.isUnauthorized()) {
      redirect('/signin');
    }
    throw error; // Let error boundary handle it
  }
}
```

### 6. Usage in Client Components

**Client Component** (`components/forms/CreateTaskForm.tsx`):

```typescript
'use client';

import { useState } from 'react';
import { apiClient, APIError } from '@/lib/api/client';
import type { TaskCreate } from '@/types/api';

interface CreateTaskFormProps {
  userId: string;
  onSuccess: () => void;
}

export function CreateTaskForm({ userId, onSuccess }: CreateTaskFormProps) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const taskData: TaskCreate = {
        title,
        priority,
      };

      await apiClient.createTask(userId, taskData);

      // Reset form
      setTitle('');
      setPriority('medium');
      onSuccess();
    } catch (err) {
      if (err instanceof APIError) {
        // Handle specific error types
        if (err.isValidationError()) {
          setError(err.message || 'Please check your input');
        } else if (err.isUnauthorized()) {
          setError('Session expired. Please sign in again.');
          // Optionally redirect to sign in
          window.location.href = '/signin';
        } else if (err.isServerError()) {
          setError('Server error. Please try again later.');
        } else {
          setError(err.message);
        }
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
        disabled={isSubmitting}
      />

      <select
        value={priority}
        onChange={(e) => setPriority(e.target.value as 'high' | 'medium' | 'low')}
        disabled={isSubmitting}
      >
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
}
```

### 7. Usage in Custom Hooks

**useTask Hook** (`lib/hooks/useTask.ts`):

```typescript
'use client';

import { useState, useEffect } from 'react';
import { apiClient, APIError } from '@/lib/api/client';
import type { Task } from '@/types/api';

export function useTask(userId: string, taskId: number) {
  const [task, setTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchTask() {
      try {
        setIsLoading(true);
        setError(null);
        const data = await apiClient.getTask(userId, taskId);

        if (isMounted) {
          setTask(data);
        }
      } catch (err) {
        if (isMounted) {
          if (err instanceof APIError) {
            setError(err.message);

            if (err.isUnauthorized()) {
              window.location.href = '/signin';
            }
          } else {
            setError('Failed to load task');
          }
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    fetchTask();

    return () => {
      isMounted = false;
    };
  }, [userId, taskId]);

  return { task, isLoading, error };
}
```

**Usage**:

```typescript
'use client';

import { useTask } from '@/lib/hooks/useTask';

export function TaskDetail({ userId, taskId }: { userId: string; taskId: number }) {
  const { task, isLoading, error } = useTask(userId, taskId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!task) return <div>Task not found</div>;

  return (
    <div>
      <h1>{task.title}</h1>
      <p>{task.description}</p>
    </div>
  );
}
```

### 8. Interceptors Pattern (Advanced)

**API Client with Interceptors** (`lib/api/client-advanced.ts`):

```typescript
type RequestInterceptor = (config: RequestInit) => RequestInit | Promise<RequestInit>;
type ResponseInterceptor = <T>(response: T) => T | Promise<T>;

class APIClientWithInterceptors {
  private baseURL: string;
  private getToken: () => Promise<string | null>;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];

  constructor(baseURL: string, getToken: () => Promise<string | null>) {
    this.baseURL = baseURL;
    this.getToken = getToken;
  }

  /**
   * Add request interceptor
   */
  addRequestInterceptor(interceptor: RequestInterceptor) {
    this.requestInterceptors.push(interceptor);
  }

  /**
   * Add response interceptor
   */
  addResponseInterceptor(interceptor: ResponseInterceptor) {
    this.responseInterceptors.push(interceptor);
  }

  /**
   * Apply all request interceptors
   */
  private async applyRequestInterceptors(
    config: RequestInit
  ): Promise<RequestInit> {
    let finalConfig = config;

    for (const interceptor of this.requestInterceptors) {
      finalConfig = await interceptor(finalConfig);
    }

    return finalConfig;
  }

  /**
   * Apply all response interceptors
   */
  private async applyResponseInterceptors<T>(response: T): Promise<T> {
    let finalResponse = response;

    for (const interceptor of this.responseInterceptors) {
      finalResponse = await interceptor(finalResponse);
    }

    return finalResponse;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Apply request interceptors
    const config = await this.applyRequestInterceptors(options);

    // Make request (same as before)
    const token = await this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...config,
      headers,
    });

    if (!response.ok) {
      await this.handleErrorResponse(response);
    }

    const data = response.status === 204 ? undefined : await response.json();

    // Apply response interceptors
    return this.applyResponseInterceptors(data as T);
  }

  // ... (rest of the methods same as APIClient)
}

// Usage example:
const client = new APIClientWithInterceptors(
  process.env.NEXT_PUBLIC_API_URL || '',
  getAuthToken
);

// Add logging interceptor
client.addRequestInterceptor((config) => {
  console.log('API Request:', config);
  return config;
});

// Add response timestamp interceptor
client.addResponseInterceptor((response) => {
  console.log('API Response received at:', new Date().toISOString());
  return response;
});
```

### 9. Mock API Client for Testing

**Mock API Client** (`lib/api/client.mock.ts`):

```typescript
import type { Task, TaskCreate, Tag } from '@/types/api';

export class MockAPIClient {
  private mockTasks: Task[] = [
    {
      id: 1,
      user_id: 'user-123',
      title: 'Test Task',
      description: 'Test description',
      completed: false,
      priority: 'medium',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      tags: [],
    },
  ];

  async getTasks(): Promise<Task[]> {
    return Promise.resolve(this.mockTasks);
  }

  async createTask(userId: string, data: TaskCreate): Promise<Task> {
    const newTask: Task = {
      id: this.mockTasks.length + 1,
      user_id: userId,
      title: data.title,
      description: data.description || '',
      completed: false,
      priority: data.priority,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      tags: [],
    };

    this.mockTasks.push(newTask);
    return Promise.resolve(newTask);
  }

  // ... implement other methods
}

export const mockApiClient = new MockAPIClient();
```

## Best Practices

1. **Single Source of Truth**: One API client for all requests
2. **Type Everything**: Use TypeScript generics for type safety
3. **Error Handling**: Create custom error class with helper methods
4. **Token Management**: Centralize authentication token handling
5. **Environment Variables**: Use env vars for API URL configuration
6. **Query Parameters**: Build query strings programmatically
7. **Request/Response Types**: Define interfaces for all API data
8. **Error Recovery**: Provide clear error messages to users
9. **Loading States**: Track loading state in components
10. **Mock Client**: Create mock client for testing

## Common Patterns

### GET Request with Query Parameters
```typescript
const tasks = await apiClient.getTasks(userId, {
  status: 'pending',
  priority: 'high,medium',
  sort_by: 'created_at',
});
```

### POST Request with Body
```typescript
const task = await apiClient.createTask(userId, {
  title: 'New Task',
  priority: 'high',
});
```

### Error Handling Pattern
```typescript
try {
  await apiClient.createTask(userId, data);
} catch (err) {
  if (err instanceof APIError) {
    if (err.isUnauthorized()) {
      redirect('/signin');
    } else if (err.isValidationError()) {
      setErrors(err.details);
    }
  }
}
```

## Success Criteria

- ✅ API client class created with private request method
- ✅ Generic request method with type parameter
- ✅ Automatic JWT token injection implemented
- ✅ Custom APIError class with helper methods
- ✅ All endpoint methods typed correctly
- ✅ Environment variables configured
- ✅ Query string builder implemented
- ✅ Error handling in all methods
- ✅ Usage examples in server and client components
- ✅ No console errors for API calls

## Related Skills

- `server_component_patterns`: Using API client in server components
- `client_component_patterns`: Using API client in client components
- `better_auth_setup`: Token management with Better Auth

## References

- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [TypeScript Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
