'use client';
import React, { useState, FormEvent } from 'react';
import { ErrorHandler } from '../lib/utils/error-handler';
import { ErrorDisplay } from './error-display';
import { LoadingSpinner } from './loading-spinner';
import { SuccessDisplay } from './success-display';

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

interface TaskFormProps {
  onTaskCreated: (task: Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => Promise<void>;
}

export const TaskForm = ({ onTaskCreated }: TaskFormProps) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (title.trim().length > 200) {
      setError('Title must be 200 characters or less');
      return;
    }

    if (description.trim().length > 1000) {
      setError('Description must be 1000 characters or less');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Call the parent function with just the required fields for optimistic creation
      // This function should return a promise that resolves when the API call completes
      await onTaskCreated({
        title: title.trim(),
        description: description.trim(),
        completed: false,
      });

      // Reset form fields only after successful API call
      setTitle('');
      setDescription('');
      // Don't set success message here since the parent component handles it
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-8">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Add New Task</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <SuccessDisplay message={success} onClose={() => setSuccess('')} />
        <ErrorDisplay error={error} onClose={() => setError('')} />
        <div className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="form-input w-full"
              placeholder="What needs to be done?"
              maxLength={200}
            />
          </div>
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="form-input w-full"
              placeholder="Add details..."
              maxLength={1000}
            />
          </div>
        </div>
        <div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" />
                <span className="ml-2">Creating...</span>
              </>
            ) : (
              'Add Task'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};