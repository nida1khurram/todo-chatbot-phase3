'use client';
import React, { useState, FormEvent } from 'react';
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
  priority: string;
  tags?: string;
  recurrence_rule?: string;
  recurrence_end_date?: string;
}

interface TaskFormProps {
  /* eslint-disable no-unused-vars */
  onTaskCreated: (task: Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => Promise<void>;
  /* eslint-enable no-unused-vars */
}

export const TaskForm = ({ onTaskCreated }: TaskFormProps) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState<string>('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [tags, setTags] = useState('');
  const [recurrenceRule, setRecurrenceRule] = useState<string>('');
  const [recurrenceEndDate, setRecurrenceEndDate] = useState<string>('');
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

    if (tags.trim().length > 200) {
      setError('Tags must be 200 characters or less');
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
        due_date: dueDate || undefined,
        priority: priority,
        tags: tags.trim() || undefined,
        recurrence_rule: recurrenceRule || undefined,
        recurrence_end_date: recurrenceEndDate || undefined,
      });

      // Reset form fields only after successful API call
      setTitle('');
      setDescription('');
      setDueDate('');
      setPriority('medium');
      setTags('');
      setRecurrenceRule('');
      setRecurrenceEndDate('');
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
                Due Date (Optional)
              </label>
              <input
                type="datetime-local"
                id="dueDate"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="form-input w-full"
              />
            </div>
            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
                className="form-input w-full"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
                Tags (comma separated, optional)
              </label>
              <input
                type="text"
                id="tags"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                className="form-input w-full"
                placeholder="work, personal, urgent..."
                maxLength={200}
              />
            </div>
            <div>
              <label htmlFor="recurrenceRule" className="block text-sm font-medium text-gray-700 mb-1">
                Recurrence (Optional)
              </label>
              <select
                id="recurrenceRule"
                value={recurrenceRule}
                onChange={(e) => setRecurrenceRule(e.target.value)}
                className="form-input w-full"
              >
                <option value="">None</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          </div>
          {recurrenceRule && (
            <div>
              <label htmlFor="recurrenceEndDate" className="block text-sm font-medium text-gray-700 mb-1">
                Recurrence End Date (Optional)
              </label>
              <input
                type="date"
                id="recurrenceEndDate"
                value={recurrenceEndDate}
                onChange={(e) => setRecurrenceEndDate(e.target.value)}
                className="form-input w-full"
              />
            </div>
          )}
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