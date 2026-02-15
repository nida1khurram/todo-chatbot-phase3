// frontend/src/lib/api/tasks.ts
export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
  due_date?: string;
  priority: string;
  tags?: string;
  recurrence_rule?: string;
  recurrence_end_date?: string;
}

export interface CreateTaskData {
  title: string;
  description: string;
  completed?: boolean;
  due_date?: string;
  priority?: string;
  tags?: string;
  recurrence_rule?: string;
  recurrence_end_date?: string;
}

export interface UpdateTaskData {
  title?: string;
  description?: string;
  completed?: boolean;
  due_date?: string;
  priority?: string;
  tags?: string;
  recurrence_rule?: string;
  recurrence_end_date?: string;
}

export const taskApi = {
  async getAll(queryParams?: string): Promise<Task[]> {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    // Build URL with query parameters if provided
    let url = `${process.env.NEXT_PUBLIC_API_URL}/tasks`;
    if (queryParams) {
      url += '?' + queryParams;
    }

    // Log for debugging

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    // Check if response is ok
    if (!response.ok) {
      // Check if the response is JSON or HTML
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch tasks');
      } else {
        // If it's not JSON, return a generic error
        throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
      }
    }

    // For successful responses, check content type before parsing JSON
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      try {
        const data = await response.json();
        return data;
      } catch (jsonError) {
        throw new Error(`Response is not valid JSON: ${response.status} ${response.statusText}`);
      }
    } else {
      // If successful response is not JSON, it's an error
      throw new Error(`Response is not valid JSON: ${response.status} ${response.statusText}`);
    }
  },

  async create(data: CreateTaskData): Promise<Task> {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...data,
        completed: data.completed ?? false,
      }),
    });

    if (!response.ok) {
      // Check if the response is JSON or HTML
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create task');
      } else {
        // If it's not JSON, return a generic error
        throw new Error(`Failed to create task: ${response.status} ${response.statusText}`);
      }
    }

    try {
      return await response.json();
    } catch (jsonError) {
      // If JSON parsing fails, return a generic error
      throw new Error(`Response is not valid JSON: ${response.status} ${response.statusText}`);
    }
  },

  async update(id: number, data: UpdateTaskData): Promise<Task> {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      // Check if the response is JSON or HTML
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update task');
      } else {
        // If it's not JSON, return a generic error
        throw new Error(`Failed to update task: ${response.status} ${response.statusText}`);
      }
    }

    try {
      return await response.json();
    } catch (jsonError) {
      // If JSON parsing fails, return a generic error
      throw new Error(`Response is not valid JSON: ${response.status} ${response.statusText}`);
    }
  },

  async delete(id: number): Promise<void> {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      // Check if the response is JSON or HTML
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete task');
      } else {
        // If it's not JSON, return a generic error
        throw new Error(`Failed to delete task: ${response.status} ${response.statusText}`);
      }
    }
  },

  async toggleCompletion(id: number, completed: boolean): Promise<Task> {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ completed: !completed }),
    });

    if (!response.ok) {
      // Check if the response is JSON or HTML
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update task');
      } else {
        // If it's not JSON, return a generic error
        throw new Error(`Failed to update task: ${response.status} ${response.statusText}`);
      }
    }

    try {
      return await response.json();
    } catch (jsonError) {
      // If JSON parsing fails, return a generic error
      throw new Error(`Response is not valid JSON: ${response.status} ${response.statusText}`);
    }
  },
};