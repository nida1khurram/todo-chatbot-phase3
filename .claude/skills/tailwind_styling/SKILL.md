# Tailwind Styling Skill

## Description
Apply Tailwind CSS utility classes for responsive design using sm:, md:, lg: breakpoints, consistent spacing with p-4, gap-4, space-y-4, proper color schemes, and mobile-first approach without custom CSS.

## When to Use
- Styling components in Next.js application
- Creating responsive layouts that work on all screen sizes
- Implementing consistent spacing and colors
- Building forms, buttons, cards, and UI elements
- Avoiding custom CSS in favor of utility-first approach

## Prerequisites
- Next.js 15+ with Tailwind CSS configured
- `tailwind.config.ts` properly set up
- `globals.css` with Tailwind directives
- TypeScript enabled

## Core Concepts

### Mobile-First Approach
- Default styles apply to mobile (base)
- `sm:` applies at 640px and up (small tablets)
- `md:` applies at 768px and up (tablets)
- `lg:` applies at 1024px and up (laptops)
- `xl:` applies at 1280px and up (desktops)
- `2xl:` applies at 1536px and up (large screens)

### Utility-First Philosophy
- Compose designs using utility classes
- No custom CSS files (except globals.css for Tailwind directives)
- Consistent spacing scale (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, etc.)
- Predefined color palette
- Reusable component patterns

## Skill Steps

### 1. Spacing System

**Padding and Margin**:
- `p-4` = padding: 1rem (16px)
- `px-4` = padding-left and padding-right: 1rem
- `py-4` = padding-top and padding-bottom: 1rem
- `pt-4` = padding-top: 1rem
- `m-4` = margin: 1rem
- `mx-auto` = margin-left and margin-right: auto (centering)
- `space-y-4` = vertical spacing between children: 1rem
- `gap-4` = gap: 1rem (for flexbox/grid)

**Common Spacing Patterns**:

```typescript
// Card with consistent padding
<div className="p-4 md:p-6 lg:p-8">
  {/* Content */}
</div>

// Container with horizontal padding and max width
<div className="px-4 md:px-6 lg:px-8 max-w-7xl mx-auto">
  {/* Content */}
</div>

// Stack of elements with vertical spacing
<div className="space-y-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

// Flexbox with gap
<div className="flex gap-4">
  <button>Cancel</button>
  <button>Submit</button>
</div>

// Grid with gap
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>
```

### 2. Responsive Layout Patterns

**Responsive Grid**:

```typescript
// Task list - 1 column on mobile, 2 on tablet, 3 on desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {tasks.map(task => (
    <TaskCard key={task.id} task={task} />
  ))}
</div>

// Dashboard layout - stacked on mobile, side-by-side on desktop
<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
  <aside className="lg:col-span-1">
    {/* Sidebar */}
  </aside>
  <main className="lg:col-span-3">
    {/* Main content */}
  </main>
</div>
```

**Responsive Flexbox**:

```typescript
// Navbar - stacked on mobile, horizontal on desktop
<nav className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4">
  <div className="text-xl font-bold">Logo</div>
  <div className="flex flex-col md:flex-row gap-4">
    <a href="/tasks">Tasks</a>
    <a href="/profile">Profile</a>
  </div>
</nav>

// Form - full width on mobile, fixed width on desktop
<form className="w-full max-w-md mx-auto space-y-4 p-4">
  {/* Form fields */}
</form>
```

**Container Pattern**:

```typescript
// Page container with responsive padding
<div className="min-h-screen bg-gray-50">
  <div className="container mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
    <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold mb-6">
      My Tasks
    </h1>
    {/* Content */}
  </div>
</div>
```

### 3. Color System

**Background Colors**:

```typescript
// Primary backgrounds
<div className="bg-blue-600 hover:bg-blue-700">Primary</div>
<div className="bg-gray-200 hover:bg-gray-300">Secondary</div>
<div className="bg-red-600 hover:bg-red-700">Danger</div>
<div className="bg-green-600 hover:bg-green-700">Success</div>

// Subtle backgrounds
<div className="bg-gray-50">Light gray background</div>
<div className="bg-white">White background</div>

// Dark mode support (optional)
<div className="bg-white dark:bg-gray-800">Adaptive background</div>
```

**Text Colors**:

```typescript
// Primary text
<h1 className="text-gray-900">Heading</h1>
<p className="text-gray-700">Body text</p>
<span className="text-gray-500">Muted text</span>

// Colored text
<span className="text-blue-600">Link</span>
<span className="text-red-600">Error</span>
<span className="text-green-600">Success</span>

// Contrast text on colored backgrounds
<div className="bg-blue-600 text-white">White text on blue</div>
```

**Border Colors**:

```typescript
<div className="border border-gray-300">Default border</div>
<div className="border-2 border-blue-600">Accent border</div>
<div className="border-t border-gray-200">Top border only</div>
```

### 4. Typography

**Heading Scale**:

```typescript
<h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900">
  Main Heading
</h1>

<h2 className="text-2xl md:text-3xl font-bold text-gray-900">
  Section Heading
</h2>

<h3 className="text-xl md:text-2xl font-semibold text-gray-900">
  Subsection Heading
</h3>

<h4 className="text-lg md:text-xl font-medium text-gray-900">
  Card Heading
</h4>
```

**Body Text**:

```typescript
// Regular paragraph
<p className="text-base text-gray-700 leading-relaxed">
  Regular body text with comfortable line height.
</p>

// Small text
<p className="text-sm text-gray-600">
  Smaller text for captions or meta information.
</p>

// Large text
<p className="text-lg text-gray-700">
  Slightly larger text for emphasis.
</p>
```

**Font Weights**:

```typescript
<span className="font-light">Light (300)</span>
<span className="font-normal">Normal (400)</span>
<span className="font-medium">Medium (500)</span>
<span className="font-semibold">Semibold (600)</span>
<span className="font-bold">Bold (700)</span>
```

### 5. Button Patterns

**Primary Button**:

```typescript
<button className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
  Primary Button
</button>
```

**Secondary Button**:

```typescript
<button className="px-4 py-2 bg-gray-200 text-gray-800 font-medium rounded-lg hover:bg-gray-300 active:bg-gray-400 disabled:opacity-50 transition-colors">
  Secondary Button
</button>
```

**Danger Button**:

```typescript
<button className="px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 active:bg-red-800 disabled:opacity-50 transition-colors">
  Delete
</button>
```

**Outline Button**:

```typescript
<button className="px-4 py-2 border-2 border-blue-600 text-blue-600 font-medium rounded-lg hover:bg-blue-50 active:bg-blue-100 transition-colors">
  Outline Button
</button>
```

**Icon Button**:

```typescript
<button className="p-2 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors">
  <svg className="w-5 h-5" />
</button>
```

**Button Sizes**:

```typescript
// Small
<button className="px-3 py-1.5 text-sm">Small</button>

// Medium (default)
<button className="px-4 py-2 text-base">Medium</button>

// Large
<button className="px-6 py-3 text-lg">Large</button>
```

### 6. Form Input Patterns

**Text Input**:

```typescript
<input
  type="text"
  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
  placeholder="Enter text..."
/>

// With error state
<input
  type="text"
  className="w-full px-4 py-2 border-2 border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
  placeholder="Enter text..."
/>
```

**Textarea**:

```typescript
<textarea
  rows={4}
  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
  placeholder="Enter description..."
/>
```

**Select Dropdown**:

```typescript
<select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white">
  <option value="low">Low Priority</option>
  <option value="medium">Medium Priority</option>
  <option value="high">High Priority</option>
</select>
```

**Checkbox**:

```typescript
<label className="flex items-center gap-2 cursor-pointer">
  <input
    type="checkbox"
    className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
  />
  <span className="text-gray-700">Remember me</span>
</label>
```

**Form Layout**:

```typescript
<form className="space-y-6 max-w-md mx-auto">
  <div>
    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
      Task Title *
    </label>
    <input
      id="title"
      type="text"
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
    />
    <p className="mt-1 text-sm text-gray-500">Maximum 200 characters</p>
  </div>

  <div>
    <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
      Priority
    </label>
    <select
      id="priority"
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
    >
      <option value="low">Low</option>
      <option value="medium">Medium</option>
      <option value="high">High</option>
    </select>
  </div>

  <div className="flex gap-3">
    <button type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
      Submit
    </button>
    <button type="button" className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">
      Cancel
    </button>
  </div>
</form>
```

### 7. Card Patterns

**Basic Card**:

```typescript
<div className="bg-white rounded-lg shadow p-6">
  <h3 className="text-xl font-semibold text-gray-900 mb-2">Card Title</h3>
  <p className="text-gray-600">Card content goes here.</p>
</div>
```

**Card with Border**:

```typescript
<div className="bg-white rounded-lg border border-gray-200 p-6">
  <h3 className="text-xl font-semibold text-gray-900 mb-2">Card Title</h3>
  <p className="text-gray-600">Card content goes here.</p>
</div>
```

**Interactive Card (Hover Effect)**:

```typescript
<div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-6">
  <h3 className="text-xl font-semibold text-gray-900 mb-2">Clickable Card</h3>
  <p className="text-gray-600">Click to view details.</p>
</div>
```

**Task Card Example**:

```typescript
<div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
  <div className="flex items-start justify-between mb-3">
    <div className="flex items-center gap-3">
      <input
        type="checkbox"
        className="w-5 h-5 text-blue-600 rounded"
        checked={task.completed}
      />
      <h4 className={`text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
        {task.title}
      </h4>
    </div>
    <button className="p-1 rounded hover:bg-gray-100">
      <svg className="w-5 h-5 text-gray-500" />
    </button>
  </div>

  <p className="text-gray-600 text-sm mb-3 line-clamp-2">
    {task.description}
  </p>

  <div className="flex items-center justify-between">
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
      task.priority === 'high' ? 'bg-red-100 text-red-700' :
      task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
      'bg-green-100 text-green-700'
    }`}>
      {task.priority}
    </span>

    <div className="flex gap-2">
      {task.tags.map(tag => (
        <span key={tag.id} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
          {tag.name}
        </span>
      ))}
    </div>
  </div>
</div>
```

### 8. Badge and Tag Patterns

**Priority Badges**:

```typescript
// High priority
<span className="px-3 py-1 bg-red-100 text-red-700 text-sm font-medium rounded-full">
  High
</span>

// Medium priority
<span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-sm font-medium rounded-full">
  Medium
</span>

// Low priority
<span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">
  Low
</span>
```

**Status Badges**:

```typescript
// Completed
<span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
  Completed
</span>

// Pending
<span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded">
  Pending
</span>
```

**Tags**:

```typescript
<div className="flex flex-wrap gap-2">
  {tags.map(tag => (
    <span key={tag.id} className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
      {tag.name}
      <button className="hover:bg-blue-200 rounded-full p-0.5">
        <svg className="w-3 h-3" />
      </button>
    </span>
  ))}
</div>
```

### 9. Modal and Overlay Patterns

**Modal Backdrop**:

```typescript
<div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
  <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
    {/* Modal content */}
  </div>
</div>
```

**Modal Header**:

```typescript
<div className="flex items-center justify-between p-6 border-b border-gray-200">
  <h2 className="text-2xl font-bold text-gray-900">Modal Title</h2>
  <button className="text-gray-500 hover:text-gray-700 text-2xl">
    ×
  </button>
</div>
```

**Modal Body**:

```typescript
<div className="p-6 space-y-4">
  {/* Modal content */}
</div>
```

**Modal Footer**:

```typescript
<div className="flex gap-3 p-6 border-t border-gray-200">
  <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
    Confirm
  </button>
  <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">
    Cancel
  </button>
</div>
```

### 10. Alert and Message Patterns

**Success Alert**:

```typescript
<div className="p-4 bg-green-50 border border-green-200 rounded-lg">
  <div className="flex items-start gap-3">
    <svg className="w-5 h-5 text-green-600 mt-0.5" />
    <div>
      <h4 className="text-sm font-medium text-green-800">Success!</h4>
      <p className="text-sm text-green-700 mt-1">
        Your task has been created successfully.
      </p>
    </div>
  </div>
</div>
```

**Error Alert**:

```typescript
<div className="p-4 bg-red-50 border border-red-200 rounded-lg">
  <div className="flex items-start gap-3">
    <svg className="w-5 h-5 text-red-600 mt-0.5" />
    <div>
      <h4 className="text-sm font-medium text-red-800">Error</h4>
      <p className="text-sm text-red-700 mt-1">
        Failed to create task. Please try again.
      </p>
    </div>
  </div>
</div>
```

**Info Alert**:

```typescript
<div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
  <div className="flex items-start gap-3">
    <svg className="w-5 h-5 text-blue-600 mt-0.5" />
    <div>
      <h4 className="text-sm font-medium text-blue-800">Information</h4>
      <p className="text-sm text-blue-700 mt-1">
        You have 5 pending tasks.
      </p>
    </div>
  </div>
</div>
```

### 11. Loading States

**Skeleton Loader**:

```typescript
<div className="animate-pulse space-y-4">
  <div className="h-8 w-48 bg-gray-200 rounded" />
  <div className="h-24 bg-gray-100 rounded-lg" />
  <div className="h-24 bg-gray-100 rounded-lg" />
  <div className="h-24 bg-gray-100 rounded-lg" />
</div>
```

**Spinner**:

```typescript
<div className="flex items-center justify-center p-8">
  <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
</div>
```

### 12. Navigation Patterns

**Top Navbar**:

```typescript
<nav className="bg-white border-b border-gray-200">
  <div className="container mx-auto px-4 md:px-6 lg:px-8">
    <div className="flex items-center justify-between h-16">
      <div className="flex items-center gap-8">
        <h1 className="text-xl font-bold text-gray-900">Todo App</h1>
        <div className="hidden md:flex gap-6">
          <a href="/tasks" className="text-gray-700 hover:text-gray-900">Tasks</a>
          <a href="/profile" className="text-gray-700 hover:text-gray-900">Profile</a>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="px-4 py-2 text-gray-700 hover:text-gray-900">
          Sign Out
        </button>
      </div>
    </div>
  </div>
</nav>
```

**Tabs**:

```typescript
<div className="border-b border-gray-200">
  <nav className="flex gap-8 px-4">
    <button className="py-4 border-b-2 border-blue-600 text-blue-600 font-medium">
      All Tasks
    </button>
    <button className="py-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
      Pending
    </button>
    <button className="py-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300">
      Completed
    </button>
  </nav>
</div>
```

## Best Practices

1. **Mobile-First**: Start with base styles for mobile, then add breakpoints
2. **Consistent Spacing**: Use the spacing scale (4, 6, 8, etc.)
3. **Hover States**: Add hover effects to interactive elements
4. **Focus States**: Always include focus:ring for keyboard navigation
5. **Transitions**: Use transition-colors for smooth state changes
6. **Shadows**: Use shadow utilities instead of custom box-shadow
7. **Rounded Corners**: Consistent border-radius (rounded-lg is common)
8. **Max Width**: Use max-w-* for readability (max-w-7xl for containers)
9. **Line Height**: Use leading-relaxed for body text
10. **Disabled States**: Always style disabled:opacity-50 and disabled:cursor-not-allowed

## Common Utility Combinations

### Centering
```typescript
// Horizontal center
<div className="mx-auto max-w-7xl">

// Vertical and horizontal center
<div className="flex items-center justify-center min-h-screen">
```

### Truncate Text
```typescript
// Single line
<p className="truncate">Long text...</p>

// Multiple lines
<p className="line-clamp-2">Long text...</p>
```

### Responsive Hide/Show
```typescript
// Hide on mobile, show on desktop
<div className="hidden md:block">Desktop only</div>

// Show on mobile, hide on desktop
<div className="block md:hidden">Mobile only</div>
```

## Success Criteria

- ✅ No custom CSS files (except globals.css with Tailwind directives)
- ✅ Mobile-first responsive design implemented
- ✅ Consistent spacing scale used throughout
- ✅ Proper color scheme with hover/focus states
- ✅ All interactive elements have hover effects
- ✅ Forms have focus states with ring
- ✅ Components use utility classes only
- ✅ Breakpoints (sm:, md:, lg:) used correctly
- ✅ Transitions added to state changes
- ✅ Accessible (proper contrast, focus indicators)

## Related Skills

- `nextjs_app_router_setup`: Initial Tailwind setup
- `client_component_patterns`: Interactive components with Tailwind
- `server_component_patterns`: Static components with Tailwind

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [Tailwind CSS Spacing Scale](https://tailwindcss.com/docs/customizing-spacing)
- [Tailwind CSS Color Palette](https://tailwindcss.com/docs/customizing-colors)
