# Client Component Patterns Skill

## Description
Create Client Components with 'use client' directive for interactivity, implement React hooks like useState and useEffect, handle user events, and manage client-side state properly.

## When to Use
- Building interactive UI components (forms, modals, dropdowns)
- Implementing client-side state management
- Handling user events (clicks, inputs, keyboard)
- Using browser APIs (localStorage, geolocation, etc.)
- Creating real-time features (websockets, polling)
- Implementing animations and transitions

## Prerequisites
- Next.js 15+ with App Router configured
- TypeScript enabled
- Understanding of React hooks
- Understanding of Server vs Client Components

## Core Concepts

### Client Components ('use client')
- Render on both client and server (hydration)
- Can use all React hooks (useState, useEffect, useContext, etc.)
- Can access browser APIs (window, document, localStorage)
- Can handle user events (onClick, onChange, onSubmit)
- Increase bundle size (JavaScript sent to browser)
- Enable interactivity and real-time updates

### When to Use Client Components
- User interactions (clicks, inputs, forms)
- State management (local component state)
- Side effects (subscriptions, timers, browser APIs)
- Custom hooks (useAuth, useLocalStorage, etc.)
- Third-party libraries requiring browser APIs
- Real-time features (polling, websockets)

## Skill Steps

### 1. Basic Client Component with State

**Interactive Button** (`components/ui/Button.tsx`):

```typescript
'use client'; // Required for useState

import { useState } from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}

export function Button({
  children,
  onClick,
  variant = 'primary',
  disabled = false
}: ButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    if (onClick) {
      setIsLoading(true);
      try {
        await onClick();
      } finally {
        setIsLoading(false);
      }
    }
  };

  const baseStyles = "px-4 py-2 rounded-lg font-medium transition-colors";
  const variantStyles = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isLoading}
      className={`${baseStyles} ${variantStyles[variant]} disabled:opacity-50`}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  );
}
```

### 2. Form Component with Controlled Inputs

**Task Creation Form** (`components/forms/CreateTaskForm.tsx`):

```typescript
'use client';

import { useState, FormEvent } from 'react';

interface CreateTaskFormProps {
  onSubmit: (task: TaskInput) => Promise<void>;
  onCancel: () => void;
}

interface TaskInput {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

export function CreateTaskForm({ onSubmit, onCancel }: CreateTaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (title.trim().length === 0) {
      setError('Title is required');
      return;
    }

    if (title.length > 200) {
      setError('Title must be less than 200 characters');
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit({ title, description, priority });
      // Reset form on success
      setTitle('');
      setDescription('');
      setPriority('medium');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2">
          Title *
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          disabled={isSubmitting}
        />
        <p className="text-sm text-gray-500 mt-1">
          {title.length}/200 characters
        </p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-2">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          maxLength={1000}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          disabled={isSubmitting}
        />
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium mb-2">
          Priority
        </label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as 'high' | 'medium' | 'low')}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          disabled={isSubmitting}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Creating...' : 'Create Task'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 disabled:opacity-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
```

### 3. Component with useEffect for Side Effects

**Task List with Filtering** (`components/tasks/TaskList.tsx`):

```typescript
'use client';

import { useState, useEffect } from 'react';
import { TaskCard } from './TaskCard';
import type { Task } from '@/types';

interface TaskListProps {
  initialTasks: Task[];
  userId: string;
}

export function TaskList({ initialTasks, userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Sync with server data when initialTasks changes
  useEffect(() => {
    setTasks(initialTasks);
  }, [initialTasks]);

  // Save filter preference to localStorage
  useEffect(() => {
    localStorage.setItem('taskFilter', filter);
  }, [filter]);

  // Load filter preference on mount
  useEffect(() => {
    const savedFilter = localStorage.getItem('taskFilter');
    if (savedFilter === 'pending' || savedFilter === 'completed') {
      setFilter(savedFilter);
    }
  }, []); // Empty dependency array = run once on mount

  // Filter tasks based on current filter and search
  const filteredTasks = tasks.filter(task => {
    // Apply status filter
    if (filter === 'pending' && task.completed) return false;
    if (filter === 'completed' && !task.completed) return false;

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        task.title.toLowerCase().includes(query) ||
        task.description.toLowerCase().includes(query)
      );
    }

    return true;
  });

  const handleToggleComplete = async (taskId: number) => {
    // Optimistic update
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, completed: !task.completed } : task
    ));

    try {
      await fetch(`/api/${userId}/tasks/${taskId}/complete`, {
        method: 'PATCH',
      });
    } catch (error) {
      // Revert on error
      setTasks(tasks);
      console.error('Failed to toggle task:', error);
    }
  };

  const handleDelete = async (taskId: number) => {
    // Optimistic update
    setTasks(tasks.filter(task => task.id !== taskId));

    try {
      await fetch(`/api/${userId}/tasks/${taskId}`, {
        method: 'DELETE',
      });
    } catch (error) {
      // Revert on error
      setTasks(tasks);
      console.error('Failed to delete task:', error);
    }
  };

  return (
    <div className="space-y-4">
      {/* Search input */}
      <input
        type="text"
        placeholder="Search tasks..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
      />

      {/* Filter buttons */}
      <div className="flex gap-2">
        {(['all', 'pending', 'completed'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Task list */}
      {filteredTasks.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No tasks found</p>
      ) : (
        filteredTasks.map(task => (
          <TaskCard
            key={task.id}
            task={task}
            onToggleComplete={handleToggleComplete}
            onDelete={handleDelete}
          />
        ))
      )}
    </div>
  );
}
```

### 4. Modal Component with Portal

**Modal Component** (`components/ui/Modal.tsx`):

```typescript
'use client';

import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle ESC key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Click outside to close
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={handleBackdropClick}
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto m-4"
      >
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>,
    document.body
  );
}
```

**Usage**:

```typescript
'use client';

import { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { CreateTaskForm } from '@/components/forms/CreateTaskForm';

export function TasksWithModal() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreateTask = async (taskData: TaskInput) => {
    await createTask(taskData);
    setIsModalOpen(false);
  };

  return (
    <div>
      <button
        onClick={() => setIsModalOpen(true)}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg"
      >
        Create Task
      </button>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Task"
      >
        <CreateTaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setIsModalOpen(false)}
        />
      </Modal>
    </div>
  );
}
```

### 5. Custom Hooks

**useLocalStorage Hook** (`lib/hooks/useLocalStorage.ts`):

```typescript
'use client';

import { useState, useEffect } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void] {
  // State to store our value
  const [storedValue, setStoredValue] = useState<T>(initialValue);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key);
      if (item) {
        setStoredValue(JSON.parse(item));
      }
    } catch (error) {
      console.error(`Error loading ${key} from localStorage:`, error);
    }
  }, [key]);

  // Save to localStorage whenever value changes
  const setValue = (value: T) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error saving ${key} to localStorage:`, error);
    }
  };

  return [storedValue, setValue];
}
```

**Usage**:

```typescript
'use client';

import { useLocalStorage } from '@/lib/hooks/useLocalStorage';

export function UserPreferences() {
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'light');
  const [sortBy, setSortBy] = useLocalStorage('sortBy', 'created_at');

  return (
    <div>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        Toggle Theme (Current: {theme})
      </button>
      <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="created_at">Created Date</option>
        <option value="priority">Priority</option>
        <option value="title">Title</option>
      </select>
    </div>
  );
}
```

**useDebounce Hook** (`lib/hooks/useDebounce.ts`):

```typescript
'use client';

import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

**Usage**:

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useDebounce } from '@/lib/hooks/useDebounce';

export function SearchTasks() {
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, 500); // 500ms delay

  useEffect(() => {
    if (debouncedQuery) {
      // API call only happens after user stops typing for 500ms
      fetchSearchResults(debouncedQuery);
    }
  }, [debouncedQuery]);

  return (
    <input
      type="text"
      value={searchQuery}
      onChange={(e) => setSearchQuery(e.target.value)}
      placeholder="Search tasks..."
    />
  );
}
```

### 6. Dropdown Component with Click Outside

**Dropdown Menu** (`components/ui/Dropdown.tsx`):

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';

interface DropdownProps {
  trigger: React.ReactNode;
  children: React.ReactNode;
}

export function Dropdown({ trigger, children }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div ref={dropdownRef} className="relative">
      <div onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </div>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          {children}
        </div>
      )}
    </div>
  );
}

export function DropdownItem({
  onClick,
  children
}: {
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left px-4 py-2 hover:bg-gray-100 text-gray-700"
    >
      {children}
    </button>
  );
}
```

**Usage**:

```typescript
'use client';

import { Dropdown, DropdownItem } from '@/components/ui/Dropdown';

export function TaskCard({ task }: { task: Task }) {
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <div className="flex justify-between items-start">
        <h3>{task.title}</h3>

        <Dropdown trigger={<button>⋮</button>}>
          <DropdownItem onClick={() => editTask(task.id)}>
            Edit
          </DropdownItem>
          <DropdownItem onClick={() => deleteTask(task.id)}>
            Delete
          </DropdownItem>
        </Dropdown>
      </div>
    </div>
  );
}
```

### 7. Toast Notifications

**Toast Context** (`lib/context/ToastContext.tsx`):

```typescript
'use client';

import { createContext, useContext, useState, useCallback } from 'react';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

interface ToastContextType {
  toasts: Toast[];
  showToast: (message: string, type: Toast['type']) => void;
  removeToast: (id: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: Toast['type']) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, showToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

function ToastContainer({
  toasts,
  onRemove
}: {
  toasts: Toast[];
  onRemove: (id: number) => void;
}) {
  return (
    <div className="fixed bottom-4 right-4 space-y-2 z-50">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`px-4 py-3 rounded-lg shadow-lg ${
            toast.type === 'success' ? 'bg-green-600' :
            toast.type === 'error' ? 'bg-red-600' :
            'bg-blue-600'
          } text-white`}
        >
          <div className="flex items-center justify-between gap-4">
            <span>{toast.message}</span>
            <button onClick={() => onRemove(toast.id)} className="text-xl">
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Usage**:

```typescript
'use client';

import { useToast } from '@/lib/context/ToastContext';

export function CreateTaskButton() {
  const { showToast } = useToast();

  const handleCreate = async () => {
    try {
      await createTask(/* ... */);
      showToast('Task created successfully!', 'success');
    } catch (error) {
      showToast('Failed to create task', 'error');
    }
  };

  return <button onClick={handleCreate}>Create Task</button>;
}
```

### 8. Optimistic Updates Pattern

**Task List with Optimistic Updates** (`components/tasks/OptimisticTaskList.tsx`):

```typescript
'use client';

import { useState, useTransition } from 'react';
import type { Task } from '@/types';

interface TaskListProps {
  initialTasks: Task[];
  userId: string;
}

export function OptimisticTaskList({ initialTasks, userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [isPending, startTransition] = useTransition();

  const toggleComplete = (taskId: number) => {
    // Optimistic update happens immediately
    const optimisticTasks = tasks.map(task =>
      task.id === taskId ? { ...task, completed: !task.completed } : task
    );

    startTransition(async () => {
      setTasks(optimisticTasks);

      try {
        const response = await fetch(`/api/${userId}/tasks/${taskId}/complete`, {
          method: 'PATCH',
        });

        if (!response.ok) {
          throw new Error('Failed to update task');
        }

        // Optionally refetch to ensure sync
        const updatedTask = await response.json();
        setTasks(tasks.map(task =>
          task.id === taskId ? updatedTask : task
        ));
      } catch (error) {
        // Revert optimistic update on error
        setTasks(tasks);
        console.error('Failed to toggle task:', error);
      }
    });
  };

  return (
    <div className={isPending ? 'opacity-50' : ''}>
      {tasks.map(task => (
        <div key={task.id} className="flex items-center gap-2 p-4 bg-white rounded">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => toggleComplete(task.id)}
            disabled={isPending}
          />
          <span className={task.completed ? 'line-through' : ''}>
            {task.title}
          </span>
        </div>
      ))}
    </div>
  );
}
```

### 9. Error Boundary Component

**Error Boundary** (`components/ErrorBoundary.tsx`):

```typescript
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-lg font-semibold text-red-800 mb-2">
            Something went wrong
          </h2>
          <p className="text-red-600">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Usage**:

```typescript
'use client';

import { ErrorBoundary } from '@/components/ErrorBoundary';
import { TaskList } from '@/components/tasks/TaskList';

export function TasksPageClient() {
  return (
    <ErrorBoundary>
      <TaskList />
    </ErrorBoundary>
  );
}
```

## Best Practices

1. **Always Add 'use client'**: Put at the top of files that need interactivity
2. **Keep Client Components Small**: Extract interactive parts only
3. **Type All Props**: Use TypeScript interfaces for prop validation
4. **Handle Loading States**: Show loading indicators during async operations
5. **Handle Error States**: Display user-friendly error messages
6. **Optimize Re-renders**: Use useMemo and useCallback when needed
7. **Clean Up Effects**: Return cleanup functions in useEffect
8. **Validate User Input**: Always validate before submitting
9. **Provide Feedback**: Use toasts, modals, or inline messages
10. **Accessibility**: Add proper ARIA labels and keyboard navigation

## Common Patterns

### Controlled Form Pattern
```typescript
const [value, setValue] = useState('');
<input value={value} onChange={(e) => setValue(e.target.value)} />
```

### Optimistic Update Pattern
```typescript
// Update UI immediately
setData(newData);
// Then sync with server
await updateServer(newData);
```

### Debounced Input Pattern
```typescript
const debouncedValue = useDebounce(searchQuery, 500);
useEffect(() => {
  search(debouncedValue);
}, [debouncedValue]);
```

### Click Outside Pattern
```typescript
useEffect(() => {
  const handleClick = (e: MouseEvent) => {
    if (ref.current && !ref.current.contains(e.target as Node)) {
      onClose();
    }
  };
  document.addEventListener('mousedown', handleClick);
  return () => document.removeEventListener('mousedown', handleClick);
}, []);
```

## Success Criteria

- ✅ 'use client' directive added to all interactive components
- ✅ React hooks used correctly (useState, useEffect, etc.)
- ✅ Event handlers properly typed and implemented
- ✅ Loading states shown during async operations
- ✅ Error states handled gracefully
- ✅ Forms have validation and error messages
- ✅ Optimistic updates for better UX
- ✅ Components are properly typed with TypeScript
- ✅ Custom hooks extracted for reusable logic
- ✅ No console errors or warnings

## Related Skills

- `server_component_patterns`: Server-side rendering and data fetching
- `nextjs_app_router_setup`: Initial Next.js setup
- `better_auth_setup`: Client-side authentication

## References

- [React Hooks Documentation](https://react.dev/reference/react)
- [Next.js Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)
- [TypeScript React Patterns](https://react-typescript-cheatsheet.netlify.app/)
