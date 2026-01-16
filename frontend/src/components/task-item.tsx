// frontend/src/components/task-item.tsx
import { useState, useRef, useEffect } from 'react';
import { ErrorDisplay } from '../components/error-display';
import { SuccessDisplay } from '../components/success-display';
import { LoadingSpinner } from '../components/loading-spinner';
import { ErrorHandler } from '../lib/utils/error-handler';

export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
  due_date?: string;
}

interface TaskItemProps {
  task: Task;
  onToggleCompletion: (id: number, completed: boolean) => void;
  onDelete: (id: number) => void;
  onUpdate: (task: Task) => void;
}

export const TaskItem = ({ task, onToggleCompletion, onDelete, onUpdate }: TaskItemProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [updating, setUpdating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const cardRef = useRef<HTMLLIElement>(null);

  const handleEdit = async () => {
    setUpdating(true);
    setError('');
    setSuccess('');

    // Frontend validation: Check if the current user can edit this task
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setError('You must be logged in to edit tasks');
      setUpdating(false);
      return;
    }

    // Validate inputs
    if (!editTitle.trim()) {
      setError('Title is required');
      setUpdating(false);
      return;
    }

    if (editTitle.trim().length > 200) {
      setError('Title must be 200 characters or less');
      setUpdating(false);
      return;
    }

    if (editDescription.trim().length > 1000) {
      setError('Description must be 1000 characters or less');
      setUpdating(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${task.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: editTitle.trim(),
          description: editDescription.trim(),
        }),
      });

      if (response.ok) {
        const updatedTask = await response.json();
        onUpdate(updatedTask);
        setIsEditing(false);
        setSuccess('Task updated successfully!');

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
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setDeleting(true);
    setError('');
    setSuccess('');

    try {
      // Frontend validation: Check if the current user can delete this task
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setError('You must be logged in to delete tasks');
        setDeleting(false);
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tasks/${task.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        onDelete(task.id);
        setSuccess('Task deleted successfully!');

        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const errorData = await response.json();
        const handledError = ErrorHandler.handle(errorData, 'Failed to delete task');
        setError(handledError.message);
        ErrorHandler.logError(errorData, 'Task deletion error');
      }
    } catch (err) {
      const handledError = ErrorHandler.handle(err, 'Failed to delete task');
      setError(handledError.message);
      ErrorHandler.logError(err, 'Task deletion error');
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Add smooth animation effects
  useEffect(() => {
    if (cardRef.current) {
      cardRef.current.style.transform = 'scale(1)';
      cardRef.current.style.opacity = '1';
    }
  }, []);

  const getPriorityColor = () => {
    if (task.completed) return 'border-green-200 bg-green-50';
    if (task.due_date) {
      const dueDate = new Date(task.due_date);
      const today = new Date();
      const timeDiff = dueDate.getTime() - today.getTime();
      const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

      if (daysDiff < 0) return 'border-red-200 bg-red-50';
      if (daysDiff === 0) return 'border-orange-200 bg-orange-50';
      if (daysDiff <= 3) return 'border-yellow-200 bg-yellow-50';
    }
    return 'border-gray-200 bg-white';
  };

  return (
    <li
      ref={cardRef}
      className={`transition-all duration-300 ease-in-out transform hover:scale-[1.02] shadow-lg rounded-xl overflow-hidden ${
        task.completed
          ? 'opacity-80 border-l-4 border-l-green-500'
          : 'border-l-4 border-l-indigo-500'
      } ${getPriorityColor()} ${
        isHovered || isFocused ? 'shadow-xl -translate-y-1' : 'shadow-md'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
    >
      <div className="p-5">
        {isEditing ? (
          <div className="space-y-4 animate-fadeIn">
            <SuccessDisplay message={success} onClose={() => setSuccess('')} />
            <ErrorDisplay error={error} onClose={() => setError('')} />
            <div className="space-y-3">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="form-input w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 shadow-sm"
                maxLength={200}
                placeholder="Task title..."
                autoFocus
              />
              <textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                className="form-input w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 shadow-sm"
                rows={3}
                maxLength={1000}
                placeholder="Task description..."
              />
            </div>
            <div className="flex flex-col sm:flex-row sm:space-x-3 space-y-2 sm:space-y-0 pt-2">
              <button
                onClick={handleEdit}
                disabled={updating}
                className="btn-primary flex items-center justify-center px-4 py-2 rounded-lg transition-all duration-200 hover:shadow-md"
              >
                {updating ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span className="ml-2">Saving...</span>
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
              <button
                onClick={() => setIsEditing(false)}
                disabled={updating}
                className="btn-secondary px-4 py-2 rounded-lg transition-all duration-200 hover:shadow-md"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
            <div className="flex items-start min-w-0 flex-1">
              <button
                onClick={() => onToggleCompletion(task.id, task.completed)}
                className={`h-6 w-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 mr-3 mt-0.5 flex-shrink-0 ${
                  task.completed
                    ? 'bg-green-500 border-green-500 text-white'
                    : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'
                }`}
                aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
              >
                {task.completed && (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>

              <div className="min-w-0 flex-1">
                <h3 className={`font-semibold text-lg mb-2 break-words transition-colors duration-200 ${
                  task.completed
                    ? 'line-through text-gray-500'
                    : 'text-gray-900 group-hover:text-indigo-700'
                }`}>
                  {task.title}
                </h3>

                {task.description && (
                  <p className={`text-gray-600 mb-3 break-words leading-relaxed ${
                    task.completed ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                    {task.description}
                  </p>
                )}

                <div className="flex flex-wrap gap-3 text-sm">
                  {task.due_date && (
                    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
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
                      Due: {formatDate(task.due_date)}
                    </div>
                  )}

                  <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Created: {formatDate(task.created_at)}
                  </div>

                  {task.completed && (
                    <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Completed
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-start lg:justify-end space-x-2 mt-2 lg:mt-0">
              <button
                onClick={() => setIsEditing(true)}
                disabled={deleting}
                className="text-sm text-indigo-600 hover:text-indigo-800 font-medium px-3 py-1.5 rounded-lg hover:bg-indigo-50 transition-all duration-200 flex items-center space-x-1"
                aria-label="Edit task"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>Edit</span>
              </button>

              <button
                onClick={handleDelete}
                disabled={deleting}
                className="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-1.5 rounded-lg hover:bg-red-50 transition-all duration-200 flex items-center space-x-1"
                aria-label="Delete task"
              >
                {deleting ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Deleting...</span>
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    <span>Delete</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {(success || error) && !isEditing && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <SuccessDisplay message={success} onClose={() => setSuccess('')} />
            <ErrorDisplay error={error} onClose={() => setError('')} />
          </div>
        )}
      </div>
    </li>
  );
};