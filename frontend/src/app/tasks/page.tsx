'use client';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { TaskItem } from '../../components/task-item';
import { TaskForm } from '../../components/task-form';
import { ErrorDisplay } from '../../components/error-display';
import { SuccessDisplay } from '../../components/success-display';
import { LoadingSpinner } from '../../components/loading-spinner';
import { ErrorHandler } from '../../lib/utils/error-handler';
import { taskApi, CreateTaskData, UpdateTaskData } from '../../lib/api/tasks';
import TodoChat from '../../components/todo-chat';

interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
  due_date?: string;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);

      const tasks = await taskApi.getAll();
      setTasks(tasks);
    } catch (err: any) {
      if (err.message && err.message.includes('401')) {
        // Token expired or invalid, redirect to login
        router.push('/login');
        return;
      }

      const handledError = ErrorHandler.handle(err, 'Failed to fetch tasks');
      setError(handledError.message);
      ErrorHandler.logError(err, 'Fetch tasks error');
    } finally {
      setLoading(false);
    }
  };

  const handleTaskCreated = (newTask: Task) => {
    setTasks([newTask, ...tasks]);
  };

  // Optimistic creation of a task
  const createTaskOptimistically = async (taskData: Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<void> => {
    // Create a temporary task with a temporary ID
    const tempId = -(Date.now()); // Use negative timestamp to distinguish from real IDs
    const tempTask: Task = {
      id: tempId,
      ...taskData,
      user_id: 0, // Will be set by backend
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Optimistically add the task to the list
    setTasks([tempTask, ...tasks]);

    try {
      const createdTask = await taskApi.create(taskData as CreateTaskData);
      // Replace the temporary task with the actual one
      setTasks(prevTasks => prevTasks.map(task =>
        task.id === tempId ? createdTask : task
      ));
      setSuccess('Task created successfully!');

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      const handledError = ErrorHandler.handle(err, 'Failed to create task');
      setError(handledError.message);
      // Remove the optimistic task
      setTasks(prevTasks => prevTasks.filter(task => task.id !== tempId));
      ErrorHandler.logError(err, 'Task creation error');
      // Re-throw the error so the form knows it failed
      throw err;
    }
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(prevTasks => prevTasks.map(task => task.id === updatedTask.id ? updatedTask : task));
  };

  // Optimistic deletion of a task
  const deleteTaskOptimistically = async (taskId: number) => {
    // Find the task to be deleted
    const taskToDelete = tasks.find(task => task.id === taskId);
    if (!taskToDelete) return;

    // Optimistically remove the task from the list
    setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));

    try {
      await taskApi.delete(taskId);
      // Only show success message after API call succeeds
      setSuccess('Task deleted successfully!');

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      const handledError = ErrorHandler.handle(err, 'Failed to delete task');
      setError(handledError.message);
      // Restore the task on error
      setTasks(prevTasks => [...prevTasks, taskToDelete]);
      ErrorHandler.logError(err, 'Task deletion error');
    }
  };

  const toggleTaskCompletion = async (taskId: number, completed: boolean) => {
    // Optimistically update the task status
    setTasks(prevTasks => prevTasks.map(task =>
      task.id === taskId ? { ...task, completed: !completed } : task
    ));

    try {
      const updatedTask = await taskApi.toggleCompletion(taskId, completed);
      // Update with the server response to ensure consistency
      setTasks(prevTasks => prevTasks.map(task =>
        task.id === taskId ? updatedTask : task
      ));
      setSuccess(`Task ${!completed ? 'completed' : 'marked as incomplete'} successfully!`);

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      const handledError = ErrorHandler.handle(err, 'Failed to update task');
      setError(handledError.message);
      // Revert the optimistic update on error
      setTasks(prevTasks => prevTasks.map(task =>
        task.id === taskId ? { ...task, completed: completed } : task
      ));
      ErrorHandler.logError(err, 'Task completion update error');
    }
  };

  const startEditingTask = (task: Task) => {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description);
  };

  const cancelEditing = () => {
    setEditingTaskId(null);
    setEditTitle('');
    setEditDescription('');
  };

  const saveEditedTask = async (taskId: number) => {
    // Frontend validation
    if (!editTitle.trim()) {
      setError('Title is required');
      return;
    }

    if (editTitle.trim().length > 200) {
      setError('Title must be 200 characters or less');
      return;
    }

    if (editDescription.trim().length > 1000) {
      setError('Description must be 1000 characters or less');
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          title: editTitle.trim(),
          description: editDescription.trim(),
        }),
      });

      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(prevTasks => prevTasks.map(task =>
          task.id === taskId ? updatedTask : task
        ));
        setSuccess('Task updated successfully!');
        cancelEditing();

        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const errorData = await response.json();
        const handledError = ErrorHandler.handle(errorData, 'Failed to update task');
        setError(handledError.message);
        ErrorHandler.logError(errorData, 'Task update error');
      }
    } catch (err) {
      const handledError = ErrorHandler.handle(err, 'Failed to update task');
      setError(handledError.message);
      ErrorHandler.logError(err, 'Task update error');
    }
  };

  // Function to refresh tasks when AI operations are performed
  const refreshTasks = async () => {
    try {
      setLoading(true);
      const refreshedTasks = await taskApi.getAll();
      setTasks(refreshedTasks);
    } catch (err: any) {
      if (err.message && err.message.includes('401')) {
        // Token expired or invalid, redirect to login
        router.push('/login');
        return;
      }

      const handledError = ErrorHandler.handle(err, 'Failed to refresh tasks');
      setError(handledError.message);
      ErrorHandler.logError(err, 'Refresh tasks error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-2xl shadow-xl p-8 flex items-center justify-center h-64">
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-indigo-500"></div>
              </div>
              <LoadingSpinner size="lg" text="Loading your tasks..." />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-6 sm:py-8">
      <div className="container max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">My Tasks</h1>
              <p className="text-gray-600 mt-1">Manage your tasks efficiently and stay organized</p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="text-sm text-gray-600 bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-2 rounded-lg border border-gray-200">
                <span className="font-medium">User ID:</span> {typeof window !== 'undefined' ? (() => {
                  const token = localStorage.getItem('auth_token');
                  if (token) {
                    try {
                      const payload = JSON.parse(atob(token.split('.')[1]));
                      return payload.sub || 'Unknown';
                    } catch {
                      return 'Unknown';
                    }
                  }
                  return 'Not logged in';
                })() : 'Loading...'}
              </div>
              <button
                onClick={() => setShowChat(!showChat)}
                className={`px-4 py-2 text-sm rounded-lg font-medium transition-all duration-200 ${
                  showChat
                    ? 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 shadow-md'
                    : 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:from-indigo-600 hover:to-purple-600 shadow-md'
                }`}
              >
                {showChat ? 'Hide AI Assistant' : 'Show AI Assistant'}
              </button>
              <button
                onClick={() => {
                  // Get the token before clearing it for the backend logout request
                  const token = localStorage.getItem('auth_token');

                  // Clear all authentication data immediately for fast logout
                  localStorage.removeItem('auth_token');

                  // Clear any cookies if they exist
                  document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';

                  // Redirect to login page immediately for instant response
                  router.push('/login');

                  // Optionally, make a background logout request to the backend
                  // but don't wait for it to complete
                  if (token) {
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
                      method: 'POST',
                      headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                      },
                    }).catch(() => {
                      // Ignore logout API errors - user is already logged out locally
                    });
                  }
                }}
                className="bg-gradient-to-r from-gray-500 to-gray-600 text-white px-4 py-2 text-sm rounded-lg font-medium hover:from-gray-600 hover:to-gray-700 transition-all duration-200 shadow-md"
              >
                Logout
              </button>
            </div>
          </div>

          <SuccessDisplay message={success} onClose={() => setSuccess('')} />
          <ErrorDisplay error={error} onClose={() => setError('')} />

          <TaskForm onTaskCreated={(taskData) => createTaskOptimistically(taskData)} />

          <div className="mt-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Task List</h2>
                <p className="text-gray-600 mt-1">Your tasks are organized in a beautiful list view</p>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm font-medium text-gray-700 bg-gradient-to-r from-blue-100 to-indigo-100 px-3 py-2 rounded-lg border border-gray-200">
                  {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
                </span>
                <span className="text-sm font-medium text-green-700 bg-green-100 px-3 py-2 rounded-lg border border-green-200">
                  {tasks.filter(t => t.completed).length} completed
                </span>
                <span className="text-sm font-medium text-yellow-700 bg-yellow-100 px-3 py-2 rounded-lg border border-yellow-200">
                  {tasks.filter(t => !t.completed).length} pending
                </span>
              </div>
            </div>

            {tasks.length === 0 ? (
              <div className="text-center py-16">
                <div className="mx-auto w-24 h-24 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mb-6">
                  <svg className="w-12 h-12 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
                <p className="text-gray-500 mb-6">Get started by creating your first task!</p>
                <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 rounded-lg border border-green-200">
                  <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Tip: Click the form above to add a new task
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  editingTaskId === task.id ? (
                    // Editing mode
                    <div
                      key={task.id}
                      className="p-4 rounded-lg border-l-4 border-l-indigo-500 bg-white shadow-md"
                    >
                      <div className="space-y-4">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                          placeholder="Task title..."
                          autoFocus
                        />
                        <textarea
                          value={editDescription}
                          onChange={(e) => setEditDescription(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                          rows={3}
                          placeholder="Task description..."
                        />
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={cancelEditing}
                            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => saveEditedTask(task.id)}
                            className="px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition-colors"
                          >
                            Save
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    // Viewing mode
                    <div
                      key={task.id}
                      className={`p-4 rounded-lg border-l-4 transition-all duration-200 hover:shadow-md ${
                        task.completed
                          ? 'border-l-green-500 bg-green-50 opacity-80'
                          : task.due_date && new Date(task.due_date) < new Date() && !task.completed
                          ? 'border-l-red-500 bg-red-50'
                          : task.due_date && new Date(task.due_date).toDateString() === new Date().toDateString()
                          ? 'border-l-orange-500 bg-orange-50'
                          : task.due_date && new Date(task.due_date) <= new Date(Date.now() + 3 * 24 * 60 * 60 * 1000) && !task.completed
                          ? 'border-l-yellow-500 bg-yellow-50'
                          : 'border-l-indigo-500 bg-white'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1 min-w-0">
                          <button
                            onClick={() => toggleTaskCompletion(task.id, task.completed)}
                            className={`h-5 w-5 rounded-full border flex items-center justify-center mt-1 flex-shrink-0 ${
                              task.completed
                                ? 'bg-green-500 border-green-500 text-white'
                                : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'
                            }`}
                            aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
                          >
                            {task.completed && (
                              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                          </button>
                          <div className="min-w-0 flex-1">
                            <h3 className={`font-medium break-words ${
                              task.completed
                                ? 'line-through text-gray-500'
                                : 'text-gray-900'
                            }`}>
                              {task.title}
                            </h3>
                            {task.description && (
                              <p className={`text-sm mt-1 break-words ${
                                task.completed ? 'text-gray-400' : 'text-gray-600'
                              }`}>
                                {task.description}
                              </p>
                            )}
                            <div className="flex flex-wrap gap-2 mt-2 text-xs">
                              {task.due_date && (
                                <span className={`inline-flex items-center px-2 py-0.5 rounded-full ${
                                  new Date(task.due_date) < new Date() && !task.completed
                                    ? 'bg-red-100 text-red-800'
                                    : new Date(task.due_date).toDateString() === new Date().toDateString()
                                    ? 'bg-orange-100 text-orange-800'
                                    : new Date(task.due_date) <= new Date(Date.now() + 3 * 24 * 60 * 60 * 1000) && !task.completed
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-blue-100 text-blue-800'
                                }`}>
                                  <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                  </svg>
                                  Due: {new Date(task.due_date).toLocaleDateString()}
                                </span>
                              )}
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-gray-100 text-gray-800">
                                <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {new Date(task.created_at).toLocaleDateString()}
                              </span>
                              {task.completed && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-green-100 text-green-800">
                                  <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                  Completed
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex space-x-2 ml-4 flex-shrink-0">
                          <button
                            onClick={() => startEditingTask(task)}
                            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium px-2 py-1 rounded hover:bg-indigo-50 transition-colors"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteTaskOptimistically(task.id)}
                            className="text-sm text-red-600 hover:text-red-800 font-medium px-2 py-1 rounded hover:bg-red-50 transition-colors"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                ))}
              </div>
            )}
          </div>

          {showChat && (
            <div className="mt-10 pt-8 border-t border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6">
              <div className="mb-6">
                <div className="flex items-center">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 mr-4">
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">Todo AI Assistant</h2>
                    <p className="text-gray-600">Chat with our AI assistant to manage your tasks efficiently</p>
                  </div>
                </div>
              </div>
              <div className="h-[500px] bg-white rounded-lg shadow-inner p-4">
                <TodoChat onTaskOperation={refreshTasks} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}