// frontend/src/lib/api/tasks.ts
import { Task } from '../../components/task-item';

export interface CreateTaskData {
  title: string;
  description: string;
  completed?: boolean;
}

export interface UpdateTaskData {
  title?: string;
  description?: string;
  completed?: boolean;
}

export const taskApi = {
  async getAll(): Promise<Task[]> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch tasks');
    }

    return response.json();
  },

  async create(data: CreateTaskData): Promise<Task> {
    const token = localStorage.getItem('auth_token');
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
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create task');
    }

    return response.json();
  },

  async update(id: number, data: UpdateTaskData): Promise<Task> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to update task');
    }

    return response.json();
  },

  async delete(id: number): Promise<void> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to delete task');
    }
  },

  async toggleCompletion(id: number, completed: boolean): Promise<Task> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ completed: !completed }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to update task');
    }

    return response.json();
  },
};