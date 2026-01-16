# Server Component Patterns Skill

## Description
Create React Server Components with async/await for data fetching, proper use of server-side rendering, passing data to client components as props, and avoiding client-side hooks in server components.

## When to Use
- Building pages that fetch data from APIs or databases
- Implementing server-side data fetching with Next.js App Router
- Optimizing performance by reducing client-side JavaScript
- Passing server-fetched data to client components
- Avoiding common server/client component mixing errors

## Prerequisites
- Next.js 15+ with App Router configured
- TypeScript enabled
- API endpoints or data sources available
- Understanding of React Server Components vs Client Components

## Core Concepts

### Server Components (Default)
- Render on the server during request or build time
- Can use async/await for data fetching
- Can access backend resources directly (databases, file systems)
- Cannot use React hooks (useState, useEffect, etc.)
- Cannot use browser APIs (window, localStorage, etc.)
- Cannot use event handlers (onClick, onChange, etc.)
- Reduce bundle size (code stays on server)

### Client Components ('use client')
- Render on client and server (hydration)
- Can use React hooks and browser APIs
- Can handle user interactions
- Receive data from server components as props
- Increase bundle size (code sent to browser)

## Skill Steps

### 1. Server Component with Data Fetching

**Basic Server Component** (`app/(dashboard)/tasks/page.tsx`):

```typescript
// This is a Server Component by default (no 'use client')
import { TaskList } from "@/components/tasks/TaskList";

// Server Components can be async
export default async function TasksPage() {
  // Direct API call on the server
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks`, {
    cache: 'no-store', // Always fetch fresh data
    headers: {
      'Authorization': `Bearer ${getServerToken()}`, // Server-side token
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }

  const tasks = await response.json();

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      {/* Pass server-fetched data to client component */}
      <TaskList initialTasks={tasks} />
    </div>
  );
}

// Helper function for server-side authentication
function getServerToken(): string {
  // Access server-side session or cookies
  // Implementation depends on your auth setup
  return process.env.SERVER_AUTH_TOKEN || '';
}
```

### 2. Passing Data to Client Components

**Server Component** (`app/(dashboard)/tasks/page.tsx`):

```typescript
import { TaskList } from "@/components/tasks/TaskList";
import { TaskFilters } from "@/components/tasks/TaskFilters";

interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'low';
  tags: string[];
}

export default async function TasksPage() {
  // Fetch data on server
  const [tasks, tags] = await Promise.all([
    fetchTasks(),
    fetchAvailableTags(),
  ]);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>

      {/* Pass server data to client components as props */}
      <TaskFilters availableTags={tags} />
      <TaskList initialTasks={tasks} />
    </div>
  );
}

async function fetchTasks(): Promise<Task[]> {
  const response = await fetch(`${process.env.API_URL}/api/tasks`, {
    cache: 'no-store',
  });
  return response.json();
}

async function fetchAvailableTags(): Promise<string[]> {
  const response = await fetch(`${process.env.API_URL}/api/tags`, {
    cache: 'no-store',
  });
  return response.json();
}
```

**Client Component** (`components/tasks/TaskList.tsx`):

```typescript
'use client'; // Required for interactivity

import { useState } from 'react';
import { TaskCard } from './TaskCard';

interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'low';
  tags: string[];
}

interface TaskListProps {
  initialTasks: Task[]; // Received from server component
}

export function TaskList({ initialTasks }: TaskListProps) {
  // Client-side state for optimistic updates
  const [tasks, setTasks] = useState<Task[]>(initialTasks);

  const handleToggleComplete = async (taskId: number) => {
    // Optimistic update
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, completed: !task.completed } : task
    ));

    // API call
    await fetch(`/api/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  };

  return (
    <div className="space-y-4">
      {tasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          onToggleComplete={handleToggleComplete}
        />
      ))}
    </div>
  );
}
```

### 3. Error Handling in Server Components

**With Error Boundary** (`app/(dashboard)/tasks/error.tsx`):

```typescript
'use client'; // Error components must be client components

export default function TasksError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-red-600 mb-4">
          Something went wrong!
        </h2>
        <p className="text-gray-600 mb-6">{error.message}</p>
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
```

**Server Component with Try-Catch** (`app/(dashboard)/tasks/page.tsx`):

```typescript
import { notFound } from 'next/navigation';

export default async function TasksPage() {
  try {
    const tasks = await fetchTasks();

    if (!tasks) {
      notFound(); // Triggers 404 page
    }

    return <TaskList initialTasks={tasks} />;
  } catch (error) {
    // This will be caught by error.tsx boundary
    throw new Error('Failed to load tasks. Please try again.');
  }
}
```

### 4. Loading States in Server Components

**Loading UI** (`app/(dashboard)/tasks/loading.tsx`):

```typescript
// This is automatically shown while page.tsx is loading
export default function TasksLoading() {
  return (
    <div className="space-y-4">
      <div className="h-8 w-48 bg-gray-200 animate-pulse rounded" />
      {[1, 2, 3].map(i => (
        <div key={i} className="h-24 bg-gray-100 animate-pulse rounded-lg" />
      ))}
    </div>
  );
}
```

### 5. Streaming with Suspense

**Server Component with Streaming** (`app/(dashboard)/dashboard/page.tsx`):

```typescript
import { Suspense } from 'react';
import { TaskStats } from '@/components/dashboard/TaskStats';
import { RecentTasks } from '@/components/dashboard/RecentTasks';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Fast component renders immediately */}
      <Suspense fallback={<StatsLoading />}>
        <TaskStats />
      </Suspense>

      {/* Slow components stream in when ready */}
      <Suspense fallback={<RecentTasksLoading />}>
        <RecentTasks />
      </Suspense>

      <Suspense fallback={<ActivityLoading />}>
        <ActivityFeed />
      </Suspense>
    </div>
  );
}

// Async server component
async function TaskStats() {
  const stats = await fetchTaskStats(); // Fast query
  return <div>{/* Render stats */}</div>;
}

// Async server component
async function RecentTasks() {
  const tasks = await fetchRecentTasks(); // Medium query
  return <div>{/* Render tasks */}</div>;
}

// Async server component
async function ActivityFeed() {
  const activity = await fetchActivityFeed(); // Slow query
  return <div>{/* Render activity */}</div>;
}
```

### 6. Data Fetching Patterns

**Parallel Data Fetching**:

```typescript
export default async function TasksPage() {
  // Fetch in parallel for better performance
  const [tasks, tags, stats] = await Promise.all([
    fetchTasks(),
    fetchTags(),
    fetchStats(),
  ]);

  return (
    <div>
      <TaskStats stats={stats} />
      <TaskFilters tags={tags} />
      <TaskList tasks={tasks} />
    </div>
  );
}
```

**Sequential Data Fetching** (when needed):

```typescript
export default async function TaskDetailPage({ params }: { params: { id: string } }) {
  // Fetch task first
  const task = await fetchTask(params.id);

  // Then fetch related data based on task
  const relatedTasks = await fetchRelatedTasks(task.tags);

  return (
    <div>
      <TaskDetail task={task} />
      <RelatedTasks tasks={relatedTasks} />
    </div>
  );
}
```

### 7. Caching Strategies

**No Cache** (always fresh data):

```typescript
const response = await fetch(url, {
  cache: 'no-store', // Equivalent to getServerSideProps
});
```

**Static Generation** (cached at build time):

```typescript
const response = await fetch(url, {
  cache: 'force-cache', // Equivalent to getStaticProps
});
```

**Revalidation** (cached with time-based refresh):

```typescript
const response = await fetch(url, {
  next: { revalidate: 60 }, // Revalidate every 60 seconds
});
```

**On-Demand Revalidation**:

```typescript
import { revalidatePath } from 'next/cache';

export async function createTask(formData: FormData) {
  'use server'; // Server Action

  // Create task in database
  await db.tasks.create({ /* ... */ });

  // Revalidate the tasks page
  revalidatePath('/tasks');
}
```

### 8. Composing Server and Client Components

**Server Component as Wrapper** (`app/(dashboard)/tasks/page.tsx`):

```typescript
import { TaskHeader } from '@/components/tasks/TaskHeader'; // Server
import { TaskList } from '@/components/tasks/TaskList'; // Client
import { TaskActions } from '@/components/tasks/TaskActions'; // Client

export default async function TasksPage() {
  const tasks = await fetchTasks();
  const user = await getCurrentUser();

  return (
    <div>
      {/* Server component (no interactivity) */}
      <TaskHeader userName={user.name} taskCount={tasks.length} />

      {/* Client component (with interactivity) */}
      <TaskActions />

      {/* Client component receiving server data */}
      <TaskList initialTasks={tasks} />
    </div>
  );
}
```

**Server Component Inside Client Component** (via children):

```typescript
// ❌ WRONG: Cannot import server component into client component
'use client';
import { ServerComponent } from './ServerComponent'; // Error!

// ✅ CORRECT: Pass server component as children
'use client';
export function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      {isOpen && children}
    </div>
  );
}

// In parent server component
<ClientWrapper>
  <ServerComponent /> {/* This works! */}
</ClientWrapper>
```

### 9. Authentication in Server Components

**Server-Side Auth Check** (`app/(dashboard)/tasks/page.tsx`):

```typescript
import { redirect } from 'next/navigation';
import { getServerSession } from '@/lib/auth/server';

export default async function TasksPage() {
  const session = await getServerSession();

  // Redirect if not authenticated
  if (!session) {
    redirect('/signin');
  }

  // Fetch user-specific data
  const tasks = await fetchTasksForUser(session.userId);

  return <TaskList initialTasks={tasks} />;
}
```

### 10. TypeScript Patterns

**Proper Typing for Server Components**:

```typescript
// Server Component (can be async)
export default async function Page({
  params,
  searchParams,
}: {
  params: { id: string };
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const task = await fetchTask(params.id);
  return <div>{task.title}</div>;
}
```

**Proper Typing for Client Components**:

```typescript
'use client';

interface TaskListProps {
  initialTasks: Task[];
  onTaskUpdate?: (taskId: number) => void;
}

export function TaskList({ initialTasks, onTaskUpdate }: TaskListProps) {
  // Client component implementation
}
```

## Common Pitfalls to Avoid

### ❌ Don't: Use hooks in server components
```typescript
// This will error!
export default async function Page() {
  const [state, setState] = useState(); // Error: Cannot use hooks in server component
  return <div />;
}
```

### ✅ Do: Use client components for hooks
```typescript
'use client';
export function InteractiveComponent() {
  const [state, setState] = useState();
  return <div />;
}
```

### ❌ Don't: Use event handlers in server components
```typescript
// This will error!
export default async function Page() {
  return <button onClick={() => {}}>Click</button>; // Error: No event handlers in server components
}
```

### ✅ Do: Extract interactive parts to client components
```typescript
// Server component
export default async function Page() {
  return <InteractiveButton />; // Client component handles click
}

// Client component
'use client';
export function InteractiveButton() {
  return <button onClick={() => {}}>Click</button>;
}
```

### ❌ Don't: Import server components into client components
```typescript
'use client';
import { ServerComponent } from './ServerComponent'; // Error!

export function ClientComponent() {
  return <ServerComponent />; // This won't work
}
```

### ✅ Do: Pass server components as children
```typescript
'use client';
export function ClientComponent({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>; // Server components can be children
}

// Usage in parent server component
<ClientComponent>
  <ServerComponent /> {/* This works */}
</ClientComponent>
```

## Best Practices

1. **Default to Server Components**: Only add 'use client' when you need interactivity
2. **Fetch Data High**: Fetch data in server components close to the root
3. **Pass Data Down**: Pass server-fetched data to client components as props
4. **Parallel Fetching**: Use Promise.all() for independent data fetches
5. **Error Boundaries**: Create error.tsx files for graceful error handling
6. **Loading States**: Create loading.tsx files for better UX
7. **Use Suspense**: Stream slow components with Suspense boundaries
8. **Type Everything**: Use TypeScript interfaces for all props
9. **Cache Wisely**: Choose appropriate caching strategy for each fetch
10. **Minimize Client JS**: Keep client components small and focused

## Success Criteria

- ✅ Server components use async/await for data fetching
- ✅ No React hooks in server components
- ✅ Data passed to client components as props
- ✅ Error boundaries implemented (error.tsx)
- ✅ Loading states implemented (loading.tsx)
- ✅ Proper 'use client' directives on interactive components
- ✅ Type-safe props between server and client components
- ✅ Appropriate caching strategies applied
- ✅ No console errors about server/client mismatches
- ✅ Fast initial page load with server-rendered content

## Example: Complete Feature Implementation

**Server Component** (`app/(dashboard)/tasks/page.tsx`):

```typescript
import { Suspense } from 'react';
import { TaskList } from '@/components/tasks/TaskList';
import { TaskFilters } from '@/components/tasks/TaskFilters';
import { CreateTaskButton } from '@/components/tasks/CreateTaskButton';
import { getServerSession } from '@/lib/auth/server';
import { redirect } from 'next/navigation';

export default async function TasksPage({
  searchParams,
}: {
  searchParams: { status?: string; priority?: string };
}) {
  // Server-side authentication
  const session = await getServerSession();
  if (!session) redirect('/signin');

  // Parallel data fetching
  const [tasks, tags] = await Promise.all([
    fetchTasks(session.userId, searchParams),
    fetchUserTags(session.userId),
  ]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Tasks</h1>
        <CreateTaskButton />
      </div>

      <TaskFilters availableTags={tags} />

      <Suspense fallback={<TaskListSkeleton />}>
        <TaskList initialTasks={tasks} userId={session.userId} />
      </Suspense>
    </div>
  );
}

async function fetchTasks(userId: string, filters: any) {
  const response = await fetch(
    `${process.env.API_URL}/api/${userId}/tasks?${new URLSearchParams(filters)}`,
    { cache: 'no-store' }
  );
  return response.json();
}

async function fetchUserTags(userId: string) {
  const response = await fetch(
    `${process.env.API_URL}/api/${userId}/tags`,
    { next: { revalidate: 300 } } // Cache for 5 minutes
  );
  return response.json();
}
```

**Client Component** (`components/tasks/TaskList.tsx`):

```typescript
'use client';

import { useState } from 'react';
import { TaskCard } from './TaskCard';
import type { Task } from '@/types';

interface TaskListProps {
  initialTasks: Task[];
  userId: string;
}

export function TaskList({ initialTasks, userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);

  const handleToggleComplete = async (taskId: number) => {
    // Optimistic update
    setTasks(tasks.map(t =>
      t.id === taskId ? { ...t, completed: !t.completed } : t
    ));

    // API call
    try {
      await fetch(`/api/${userId}/tasks/${taskId}/complete`, {
        method: 'PATCH',
      });
    } catch (error) {
      // Revert on error
      setTasks(tasks);
    }
  };

  return (
    <div className="space-y-4">
      {tasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          onToggleComplete={handleToggleComplete}
        />
      ))}
    </div>
  );
}
```

## Related Skills

- `nextjs_app_router_setup`: Initial Next.js setup
- `api_client_setup`: Create API client utilities
- `better_auth_setup`: Server-side authentication

## References

- [React Server Components](https://react.dev/blog/2023/03/22/react-labs-what-we-have-been-working-on-march-2023#react-server-components)
- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Next.js Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching)
