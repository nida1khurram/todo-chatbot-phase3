---
name: in_memory_storage
description: Implement in-memory storage classes using typed dictionaries with methods for add, get, get_all, update, and delete operations, auto-incrementing IDs, and proper Optional return types.
---

# In-Memory Storage Skill

You are an expert at implementing type-safe in-memory storage classes for Python applications with proper CRUD operations and ID management.

## When to Use This Skill

Apply this skill when the user:
- Needs temporary data storage for a CLI application
- Wants to prototype before adding a database
- Needs a simple storage layer for testing
- Wants type-safe dictionary-based storage
- Needs CRUD operations with auto-incrementing IDs

## Basic Storage Pattern

### Generic In-Memory Store

```python
"""Generic type-safe in-memory storage."""

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class InMemoryStore(Generic[T]):
    """Generic in-memory storage with CRUD operations."""

    def __init__(self) -> None:
        self._data: dict[int, T] = {}
        self._next_id: int = 1

    def add(self, item: T) -> T:
        """Add item and assign auto-incremented ID."""
        # Assumes item has an 'id' field that can be set
        item_dict = item.model_dump()
        item_dict["id"] = self._next_id
        new_item = type(item).model_validate(item_dict)
        self._data[self._next_id] = new_item
        self._next_id += 1
        return new_item

    def get(self, item_id: int) -> T | None:
        """Get item by ID, returns None if not found."""
        return self._data.get(item_id)

    def get_all(self) -> list[T]:
        """Get all items as a list."""
        return list(self._data.values())

    def update(self, item_id: int, item: T) -> T | None:
        """Update existing item, returns None if not found."""
        if item_id not in self._data:
            return None
        item_dict = item.model_dump()
        item_dict["id"] = item_id
        updated_item = type(item).model_validate(item_dict)
        self._data[item_id] = updated_item
        return updated_item

    def delete(self, item_id: int) -> bool:
        """Delete item by ID, returns True if deleted."""
        if item_id in self._data:
            del self._data[item_id]
            return True
        return False

    def exists(self, item_id: int) -> bool:
        """Check if item exists."""
        return item_id in self._data

    def count(self) -> int:
        """Get total number of items."""
        return len(self._data)

    def clear(self) -> None:
        """Remove all items and reset ID counter."""
        self._data.clear()
        self._next_id = 1
```

## Typed Storage for Specific Models

### Todo Storage Example

```python
"""Typed storage for Todo items."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Todo priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoCreate(BaseModel):
    """Model for creating a todo (no ID)."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None


class TodoUpdate(BaseModel):
    """Model for updating a todo (all optional)."""
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    due_date: datetime | None = None
    completed: bool | None = None


class Todo(BaseModel):
    """Complete todo model with ID."""
    id: int
    title: str
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TodoStorage:
    """In-memory storage specifically for Todo items."""

    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1

    def add(self, todo_create: TodoCreate) -> Todo:
        """Create a new todo with auto-generated ID."""
        now = datetime.now()
        todo = Todo(
            id=self._next_id,
            title=todo_create.title,
            description=todo_create.description,
            priority=todo_create.priority,
            due_date=todo_create.due_date,
            completed=False,
            created_at=now,
            updated_at=now,
        )
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    def get(self, todo_id: int) -> Todo | None:
        """Get todo by ID."""
        return self._todos.get(todo_id)

    def get_all(self) -> list[Todo]:
        """Get all todos."""
        return list(self._todos.values())

    def update(self, todo_id: int, todo_update: TodoUpdate) -> Todo | None:
        """Update todo with provided fields."""
        existing = self._todos.get(todo_id)
        if existing is None:
            return None

        # Only update fields that are provided (not None)
        update_data = todo_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now()

        updated_todo = existing.model_copy(update=update_data)
        self._todos[todo_id] = updated_todo
        return updated_todo

    def delete(self, todo_id: int) -> bool:
        """Delete todo by ID."""
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False

    def exists(self, todo_id: int) -> bool:
        """Check if todo exists."""
        return todo_id in self._todos

    def count(self) -> int:
        """Get total count of todos."""
        return len(self._todos)

    def clear(self) -> None:
        """Clear all todos."""
        self._todos.clear()
        self._next_id = 1

    # Query methods
    def get_by_status(self, completed: bool) -> list[Todo]:
        """Get todos by completion status."""
        return [t for t in self._todos.values() if t.completed == completed]

    def get_by_priority(self, priority: Priority) -> list[Todo]:
        """Get todos by priority."""
        return [t for t in self._todos.values() if t.priority == priority]

    def get_pending(self) -> list[Todo]:
        """Get all incomplete todos."""
        return self.get_by_status(completed=False)

    def get_completed(self) -> list[Todo]:
        """Get all completed todos."""
        return self.get_by_status(completed=True)

    def get_overdue(self) -> list[Todo]:
        """Get overdue incomplete todos."""
        now = datetime.now()
        return [
            t for t in self._todos.values()
            if not t.completed and t.due_date and t.due_date < now
        ]

    def search(self, query: str) -> list[Todo]:
        """Search todos by title or description."""
        query_lower = query.lower()
        return [
            t for t in self._todos.values()
            if query_lower in t.title.lower()
            or (t.description and query_lower in t.description.lower())
        ]
```

## Abstract Storage Interface

### Protocol-Based Interface

```python
"""Abstract storage interface using Protocol."""

from typing import Protocol, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)


class StorageProtocol(Protocol[T, CreateT, UpdateT]):
    """Protocol defining storage operations."""

    def add(self, item: CreateT) -> T:
        """Add a new item."""
        ...

    def get(self, item_id: int) -> T | None:
        """Get item by ID."""
        ...

    def get_all(self) -> list[T]:
        """Get all items."""
        ...

    def update(self, item_id: int, item: UpdateT) -> T | None:
        """Update an item."""
        ...

    def delete(self, item_id: int) -> bool:
        """Delete an item."""
        ...

    def exists(self, item_id: int) -> bool:
        """Check if item exists."""
        ...

    def count(self) -> int:
        """Get item count."""
        ...

    def clear(self) -> None:
        """Clear all items."""
        ...
```

### Abstract Base Class

```python
"""Abstract storage using ABC."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)


class AbstractStorage(ABC, Generic[T, CreateT, UpdateT]):
    """Abstract base class for storage implementations."""

    @abstractmethod
    def add(self, item: CreateT) -> T:
        """Add a new item and return it with assigned ID."""
        pass

    @abstractmethod
    def get(self, item_id: int) -> T | None:
        """Get item by ID, returns None if not found."""
        pass

    @abstractmethod
    def get_all(self) -> list[T]:
        """Get all items."""
        pass

    @abstractmethod
    def update(self, item_id: int, item: UpdateT) -> T | None:
        """Update item, returns None if not found."""
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        """Delete item, returns True if deleted."""
        pass

    def exists(self, item_id: int) -> bool:
        """Check if item exists."""
        return self.get(item_id) is not None

    @abstractmethod
    def count(self) -> int:
        """Get total item count."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all items."""
        pass
```

## Storage with Filtering and Sorting

```python
"""Storage with advanced querying capabilities."""

from datetime import datetime
from enum import Enum
from typing import Callable
from pydantic import BaseModel, Field


class SortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


class Todo(BaseModel):
    """Todo model."""
    id: int
    title: str
    priority: str
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class TodoStorageAdvanced:
    """Storage with filtering, sorting, and pagination."""

    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1

    def add(self, title: str, priority: str = "medium") -> Todo:
        """Add a new todo."""
        todo = Todo(
            id=self._next_id,
            title=title,
            priority=priority,
        )
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    def get(self, todo_id: int) -> Todo | None:
        """Get todo by ID."""
        return self._todos.get(todo_id)

    def get_all(
        self,
        *,
        filter_fn: Callable[[Todo], bool] | None = None,
        sort_by: str | None = None,
        sort_order: SortOrder = SortOrder.ASC,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Todo]:
        """
        Get todos with optional filtering, sorting, and pagination.

        Args:
            filter_fn: Optional function to filter todos
            sort_by: Field name to sort by (e.g., "created_at", "title")
            sort_order: Sort direction (asc or desc)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of filtered, sorted, paginated todos
        """
        # Start with all todos
        result = list(self._todos.values())

        # Apply filter
        if filter_fn:
            result = [t for t in result if filter_fn(t)]

        # Apply sorting
        if sort_by:
            reverse = sort_order == SortOrder.DESC
            result.sort(
                key=lambda t: getattr(t, sort_by, ""),
                reverse=reverse,
            )

        # Apply pagination
        if offset:
            result = result[offset:]
        if limit:
            result = result[:limit]

        return result

    def query(self) -> "TodoQuery":
        """Start a fluent query."""
        return TodoQuery(self)

    # ... standard CRUD methods ...


class TodoQuery:
    """Fluent query builder for todos."""

    def __init__(self, storage: TodoStorageAdvanced) -> None:
        self._storage = storage
        self._filters: list[Callable[[Todo], bool]] = []
        self._sort_by: str | None = None
        self._sort_order: SortOrder = SortOrder.ASC
        self._limit: int | None = None
        self._offset: int = 0

    def where(self, filter_fn: Callable[[Todo], bool]) -> "TodoQuery":
        """Add a filter condition."""
        self._filters.append(filter_fn)
        return self

    def completed(self, value: bool = True) -> "TodoQuery":
        """Filter by completion status."""
        return self.where(lambda t: t.completed == value)

    def priority(self, value: str) -> "TodoQuery":
        """Filter by priority."""
        return self.where(lambda t: t.priority == value)

    def title_contains(self, text: str) -> "TodoQuery":
        """Filter by title containing text."""
        text_lower = text.lower()
        return self.where(lambda t: text_lower in t.title.lower())

    def order_by(self, field: str, order: SortOrder = SortOrder.ASC) -> "TodoQuery":
        """Set sort field and order."""
        self._sort_by = field
        self._sort_order = order
        return self

    def limit(self, count: int) -> "TodoQuery":
        """Limit number of results."""
        self._limit = count
        return self

    def offset(self, count: int) -> "TodoQuery":
        """Skip number of results."""
        self._offset = count
        return self

    def execute(self) -> list[Todo]:
        """Execute the query and return results."""
        def combined_filter(todo: Todo) -> bool:
            return all(f(todo) for f in self._filters)

        filter_fn = combined_filter if self._filters else None

        return self._storage.get_all(
            filter_fn=filter_fn,
            sort_by=self._sort_by,
            sort_order=self._sort_order,
            limit=self._limit,
            offset=self._offset,
        )

    def first(self) -> Todo | None:
        """Get first result or None."""
        results = self.limit(1).execute()
        return results[0] if results else None

    def count(self) -> int:
        """Count matching results (ignores limit/offset)."""
        def combined_filter(todo: Todo) -> bool:
            return all(f(todo) for f in self._filters)

        filter_fn = combined_filter if self._filters else None
        return len(self._storage.get_all(filter_fn=filter_fn))


# Usage example
storage = TodoStorageAdvanced()
storage.add("Buy groceries", "high")
storage.add("Write report", "medium")
storage.add("Call mom", "low")

# Fluent query
high_priority = (
    storage.query()
    .priority("high")
    .completed(False)
    .order_by("created_at", SortOrder.DESC)
    .execute()
)
```

## Storage with Events/Callbacks

```python
"""Storage with event callbacks for reactivity."""

from datetime import datetime
from enum import Enum
from typing import Callable
from pydantic import BaseModel


class StorageEvent(str, Enum):
    """Storage event types."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    CLEARED = "cleared"


class Todo(BaseModel):
    """Todo model."""
    id: int
    title: str
    completed: bool = False


EventCallback = Callable[[StorageEvent, Todo | None], None]


class ObservableTodoStorage:
    """Storage with event notifications."""

    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1
        self._callbacks: list[EventCallback] = []

    def subscribe(self, callback: EventCallback) -> Callable[[], None]:
        """
        Subscribe to storage events.

        Returns unsubscribe function.
        """
        self._callbacks.append(callback)
        return lambda: self._callbacks.remove(callback)

    def _notify(self, event: StorageEvent, todo: Todo | None = None) -> None:
        """Notify all subscribers of an event."""
        for callback in self._callbacks:
            callback(event, todo)

    def add(self, title: str) -> Todo:
        """Add todo and notify subscribers."""
        todo = Todo(id=self._next_id, title=title)
        self._todos[self._next_id] = todo
        self._next_id += 1
        self._notify(StorageEvent.CREATED, todo)
        return todo

    def update(self, todo_id: int, **updates) -> Todo | None:
        """Update todo and notify subscribers."""
        if todo_id not in self._todos:
            return None
        todo = self._todos[todo_id]
        updated = todo.model_copy(update=updates)
        self._todos[todo_id] = updated
        self._notify(StorageEvent.UPDATED, updated)
        return updated

    def delete(self, todo_id: int) -> bool:
        """Delete todo and notify subscribers."""
        if todo_id not in self._todos:
            return False
        todo = self._todos.pop(todo_id)
        self._notify(StorageEvent.DELETED, todo)
        return True

    def clear(self) -> None:
        """Clear all and notify subscribers."""
        self._todos.clear()
        self._next_id = 1
        self._notify(StorageEvent.CLEARED)

    def get(self, todo_id: int) -> Todo | None:
        """Get todo by ID."""
        return self._todos.get(todo_id)

    def get_all(self) -> list[Todo]:
        """Get all todos."""
        return list(self._todos.values())


# Usage
storage = ObservableTodoStorage()

def on_change(event: StorageEvent, todo: Todo | None) -> None:
    print(f"Event: {event.value}, Todo: {todo}")

unsubscribe = storage.subscribe(on_change)
storage.add("Test")  # Prints: Event: created, Todo: id=1 title='Test' ...
unsubscribe()  # Stop receiving events
```

## Singleton Storage Pattern

```python
"""Singleton pattern for global storage access."""

from threading import Lock
from pydantic import BaseModel


class Todo(BaseModel):
    """Todo model."""
    id: int
    title: str
    completed: bool = False


class TodoStorage:
    """Singleton in-memory storage."""

    _instance: "TodoStorage | None" = None
    _lock: Lock = Lock()

    def __new__(cls) -> "TodoStorage":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "TodoStorage":
        """Get the singleton instance."""
        return cls()

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (useful for testing)."""
        with cls._lock:
            cls._instance = None

    # ... standard CRUD methods ...


# Usage - same instance everywhere
storage1 = TodoStorage()
storage2 = TodoStorage()
assert storage1 is storage2  # True
```

## Testing Storage

```python
"""Test examples for storage classes."""

import pytest
from datetime import datetime


class TestTodoStorage:
    """Tests for TodoStorage."""

    @pytest.fixture
    def storage(self) -> TodoStorage:
        """Create fresh storage for each test."""
        return TodoStorage()

    def test_add_assigns_auto_id(self, storage: TodoStorage) -> None:
        """Test that add assigns incrementing IDs."""
        todo1 = storage.add(TodoCreate(title="First"))
        todo2 = storage.add(TodoCreate(title="Second"))

        assert todo1.id == 1
        assert todo2.id == 2

    def test_get_returns_none_for_missing(self, storage: TodoStorage) -> None:
        """Test get returns None for non-existent ID."""
        result = storage.get(999)
        assert result is None

    def test_get_returns_todo(self, storage: TodoStorage) -> None:
        """Test get returns correct todo."""
        created = storage.add(TodoCreate(title="Test"))
        retrieved = storage.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test"

    def test_update_modifies_todo(self, storage: TodoStorage) -> None:
        """Test update modifies existing todo."""
        created = storage.add(TodoCreate(title="Original"))
        updated = storage.update(
            created.id,
            TodoUpdate(title="Modified")
        )

        assert updated is not None
        assert updated.title == "Modified"
        assert storage.get(created.id).title == "Modified"

    def test_update_returns_none_for_missing(self, storage: TodoStorage) -> None:
        """Test update returns None for non-existent ID."""
        result = storage.update(999, TodoUpdate(title="Test"))
        assert result is None

    def test_delete_removes_todo(self, storage: TodoStorage) -> None:
        """Test delete removes todo."""
        created = storage.add(TodoCreate(title="To Delete"))

        result = storage.delete(created.id)

        assert result is True
        assert storage.get(created.id) is None

    def test_delete_returns_false_for_missing(self, storage: TodoStorage) -> None:
        """Test delete returns False for non-existent ID."""
        result = storage.delete(999)
        assert result is False

    def test_get_all_returns_all_todos(self, storage: TodoStorage) -> None:
        """Test get_all returns all todos."""
        storage.add(TodoCreate(title="First"))
        storage.add(TodoCreate(title="Second"))

        todos = storage.get_all()

        assert len(todos) == 2

    def test_clear_removes_all_and_resets_id(self, storage: TodoStorage) -> None:
        """Test clear removes all todos and resets ID."""
        storage.add(TodoCreate(title="First"))
        storage.add(TodoCreate(title="Second"))

        storage.clear()

        assert storage.count() == 0
        new_todo = storage.add(TodoCreate(title="After Clear"))
        assert new_todo.id == 1  # ID reset
```

## Validation Checklist

```markdown
## In-Memory Storage Checklist

### Core Operations
- [ ] add() assigns auto-incrementing ID
- [ ] get() returns item or None
- [ ] get_all() returns list of all items
- [ ] update() modifies existing item
- [ ] delete() removes item and returns bool
- [ ] exists() checks if ID exists
- [ ] count() returns total items
- [ ] clear() removes all and resets ID

### Type Safety
- [ ] Proper type hints on all methods
- [ ] Generic types for reusable storage
- [ ] Pydantic models for data validation
- [ ] Optional return types where appropriate

### Edge Cases
- [ ] Returns None for missing items (not exception)
- [ ] Returns False for delete of missing item
- [ ] Handles empty storage gracefully
- [ ] ID counter resets on clear

### Testing
- [ ] Tests for all CRUD operations
- [ ] Tests for edge cases (missing IDs)
- [ ] Fresh storage fixture for isolation
```
