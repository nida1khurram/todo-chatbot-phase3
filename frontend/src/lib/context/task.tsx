// frontend/src/lib/context/task.tsx
'use client';

import { createContext, useContext, ReactNode, useState, useEffect } from 'react';
import { Task } from '../../components/task-item';
import { taskApi } from '../api/tasks';

interface TaskContextType {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (taskData: { title: string; description: string }) => Promise<void>;
  updateTask: (id: number, taskData: { title?: string; description?: string; completed?: boolean }) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
  toggleTaskCompletion: (id: number, completed: boolean) => Promise<void>;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

interface TaskProviderProps {
  children: ReactNode;
}

export function TaskProvider({ children }: TaskProviderProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const tasksData = await taskApi.getAll();
      setTasks(tasksData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (taskData: { title: string; description: string }): Promise<void> => {
    setError(null);

    // Create a temporary task with a temporary ID for optimistic update
    const tempId = Date.now(); // Use timestamp as temporary ID
    const tempTask = {
      id: tempId,
      ...taskData,
      completed: false,
      user_id: 1, // This would be the current user's ID from context
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Add the temporary task to the UI immediately
    setTasks([tempTask, ...tasks]);

    try {
      const newTask = await taskApi.create(taskData);
      // Replace the temporary task with the actual task from the server
      setTasks(prevTasks => prevTasks.map(task =>
        task.id === tempId ? newTask : task
      ));
    } catch (err) {
      // Remove the temporary task if the API call fails
      setTasks(prevTasks => prevTasks.filter(task => task.id !== tempId));
      setError(err instanceof Error ? err.message : 'Failed to create task');
      console.error('Error creating task:', err);
      // Re-throw the error so callers know it failed
      throw err;
    }
  };

  const updateTask = async (id: number, taskData: { title?: string; description?: string; completed?: boolean }) => {
    setError(null);

    // Optimistic update: update the task in the UI immediately
    const prevTasks = [...tasks];
    setTasks(prevTasks => prevTasks.map(task =>
      task.id === id ? { ...task, ...taskData } : task
    ));

    try {
      const updatedTask = await taskApi.update(id, taskData);
      // Update with the server response to ensure consistency
      setTasks(prevTasks => prevTasks.map(task =>
        task.id === id ? updatedTask : task
      ));
    } catch (err) {
      // Rollback to previous state if the API call fails
      setTasks(prevTasks);
      setError(err instanceof Error ? err.message : 'Failed to update task');
      console.error('Error updating task:', err);
    }
  };

  const deleteTask = async (id: number) => {
    setError(null);

    // Optimistic update: remove the task from the UI immediately
    const prevTasks = [...tasks];
    setTasks(prevTasks => prevTasks.filter(task => task.id !== id));

    try {
      await taskApi.delete(id);
      // Task was successfully deleted, state is already updated
    } catch (err) {
      // Rollback to previous state if the API call fails
      setTasks(prevTasks);
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      console.error('Error deleting task:', err);
    }
  };

  const toggleTaskCompletion = async (id: number, completed: boolean) => {
    setError(null);

    // Optimistic update: toggle the completion status in the UI immediately
    const prevTasks = [...tasks];
    setTasks(prevTasks => prevTasks.map(task =>
      task.id === id ? { ...task, completed: !completed } : task
    ));

    try {
      const updatedTask = await taskApi.toggleCompletion(id, completed);
      // Update with the server response to ensure consistency
      setTasks(prevTasks => prevTasks.map(task =>
        task.id === id ? updatedTask : task
      ));
    } catch (err) {
      // Rollback to previous state if the API call fails
      setTasks(prevTasks);
      setError(err instanceof Error ? err.message : 'Failed to update task');
      console.error('Error updating task:', err);
    }
  };

  // Fetch tasks on initial load
  useEffect(() => {
    fetchTasks();
  }, []);

  const value = {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
  };

  return <TaskContext.Provider value={value}>{children}</TaskContext.Provider>;
}

export function useTask() {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTask must be used within a TaskProvider');
  }
  return context;
}