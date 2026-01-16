# SQLModel Schema Design Skill

## Description
Create SQLModel classes with table=True for database models, define columns with proper types and constraints, add indexes on frequently queried fields, implement foreign key relationships, and include created_at/updated_at timestamps.

## When to Use
- Creating database models for FastAPI application
- Defining table schemas with SQLModel ORM
- Setting up foreign key relationships between tables
- Adding indexes for query performance optimization
- Implementing timestamp tracking for records

## Prerequisites
- FastAPI project set up
- SQLModel and asyncpg installed
- Database connection configured
- Understanding of SQL and relational databases
- PostgreSQL database available (Neon)

## Core Concepts

### SQLModel Fundamentals
- Combines Pydantic and SQLAlchemy
- `table=True` creates database table
- Type hints define column types
- Field() for constraints and metadata
- Automatic validation with Pydantic
- Native async support with asyncpg

### Column Types Mapping
- `str` → VARCHAR
- `int` → INTEGER
- `bool` → BOOLEAN
- `datetime` → TIMESTAMP
- `Optional[type]` → nullable column
- `Enum` → PostgreSQL ENUM type

### Relationships
- One-to-Many: `user_id` foreign key
- Many-to-Many: junction table with two foreign keys
- Cascade delete: `ondelete="CASCADE"`
- Lazy loading vs eager loading

## Skill Steps

### 1. Create User Model (Better Auth Compatible)

**models/user.py**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .tag import Tag


class User(SQLModel, table=True):
    """
    User model - compatible with Better Auth
    Better Auth manages this table, we just query it
    """

    __tablename__ = "user"

    # Primary key - Better Auth uses TEXT for user IDs
    id: str = Field(primary_key=True)

    # Basic user information
    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=255)
    email_verified: bool = Field(default=False)

    # Password (hashed by Better Auth)
    password: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (for querying only, not enforced by Better Auth)
    tasks: list["Task"] = Relationship(back_populates="user")
    tags: list["Tag"] = Relationship(back_populates="user")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123abc",
                "name": "John Doe",
                "email": "john@example.com",
                "email_verified": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
```

### 2. Create Task Model with Indexes

**models/task.py**:

```python
from sqlmodel import SQLModel, Field, Relationship, Column, String, Index
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .tag import Tag
    from .task_tag import TaskTag


class PriorityEnum(str, Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Task(SQLModel, table=True):
    """
    Task model with proper indexes and constraints
    """

    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to user
    user_id: str = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,  # Index for user_id queries
    )

    # Task fields with constraints
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        index=True,  # Index for search and sorting
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,  # Index for filtering by status
    )

    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        nullable=False,
        sa_column=Column(String, nullable=False, server_default="medium"),
        index=True,  # Index for filtering and sorting by priority
    )

    # Timestamps with auto-update
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,  # Index for sorting by creation date
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    task_tags: list["TaskTag"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123abc",
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the API",
                "completed": False,
                "priority": "high",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }


# Composite indexes for common query patterns
Index(
    "idx_tasks_user_completed",
    Task.user_id,
    Task.completed,
)

Index(
    "idx_tasks_user_priority",
    Task.user_id,
    Task.priority,
)

Index(
    "idx_tasks_user_created",
    Task.user_id,
    Task.created_at.desc(),
)
```

### 3. Create Tag Model

**models/tag.py**:

```python
from sqlmodel import SQLModel, Field, Relationship, Index
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .task_tag import TaskTag


class Tag(SQLModel, table=True):
    """
    Tag model for categorizing tasks
    """

    __tablename__ = "tags"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to user
    user_id: str = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
    )

    # Tag name with unique constraint per user
    name: str = Field(
        min_length=1,
        max_length=50,
        nullable=False,
        index=True,  # Index for autocomplete queries
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user: "User" = Relationship(back_populates="tags")
    task_tags: list["TaskTag"] = Relationship(
        back_populates="tag",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123abc",
                "name": "work",
                "created_at": "2024-01-01T00:00:00",
            }
        }


# Unique constraint: user can't have duplicate tag names
Index(
    "idx_tags_user_name_unique",
    Tag.user_id,
    Tag.name,
    unique=True,
)

# Index for autocomplete: LIKE queries on name
Index(
    "idx_tags_name_pattern",
    Tag.name,
    postgresql_ops={"name": "text_pattern_ops"},
)
```

### 4. Create Junction Table for Many-to-Many Relationship

**models/task_tag.py**:

```python
from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .tag import Tag


class TaskTag(SQLModel, table=True):
    """
    Junction table for many-to-many relationship between tasks and tags
    """

    __tablename__ = "task_tags"

    # Composite primary key
    task_id: int = Field(
        foreign_key="tasks.id",
        primary_key=True,
        ondelete="CASCADE",  # Delete task_tag when task is deleted
    )

    tag_id: int = Field(
        foreign_key="tags.id",
        primary_key=True,
        ondelete="CASCADE",  # Delete task_tag when tag is deleted
    )

    # Relationships
    task: "Task" = Relationship(back_populates="task_tags")
    tag: "Tag" = Relationship(back_populates="task_tags")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "tag_id": 2,
            }
        }


# Indexes for efficient lookups
Index("idx_task_tags_task", TaskTag.task_id)
Index("idx_task_tags_tag", TaskTag.tag_id)
```

### 5. Update models/__init__.py

**models/__init__.py**:

```python
"""Database models package"""

from .user import User
from .task import Task, PriorityEnum
from .tag import Tag
from .task_tag import TaskTag

# Export all models for easy importing
__all__ = [
    "User",
    "Task",
    "PriorityEnum",
    "Tag",
    "TaskTag",
]
```

### 6. Create Database Migration Utility

**core/database.py** (enhanced):

```python
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from .config.settings import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
)

# Async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in SQLModel.metadata
    """
    # Import all models to register them with SQLModel
    from models import User, Task, Tag, TaskTag

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ All tables created successfully")


async def drop_db() -> None:
    """
    Drop all database tables.
    ⚠️ WARNING: This will delete all data!
    """
    from models import User, Task, Tag, TaskTag

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        print("⚠️ All tables dropped")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    Usage: session: AsyncSession = Depends(get_session)
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 7. Add Timestamp Auto-Update Trigger (PostgreSQL)

**migrations/001_add_updated_at_trigger.sql**:

```sql
-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to tasks table
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to user table (if managing timestamps)
CREATE TRIGGER update_user_updated_at
    BEFORE UPDATE ON user
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 8. Create Model Usage Examples

**Example: Creating a Task with Tags**:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Task, Tag, TaskTag, PriorityEnum


async def create_task_with_tags(
    session: AsyncSession,
    user_id: str,
    title: str,
    description: str,
    priority: PriorityEnum,
    tag_ids: list[int],
) -> Task:
    """Create a task and associate it with tags"""

    # Create task
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
    )

    session.add(task)
    await session.flush()  # Get task.id without committing

    # Create task-tag associations
    for tag_id in tag_ids:
        task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
        session.add(task_tag)

    await session.commit()
    await session.refresh(task)

    return task
```

**Example: Querying Tasks with Filters**:

```python
from sqlalchemy import select, and_, or_
from models import Task, TaskTag, Tag


async def get_filtered_tasks(
    session: AsyncSession,
    user_id: str,
    completed: Optional[bool] = None,
    priority: Optional[PriorityEnum] = None,
    tag_ids: Optional[list[int]] = None,
    search: Optional[str] = None,
) -> list[Task]:
    """Get tasks with filters using indexes"""

    # Base query
    query = select(Task).where(Task.user_id == user_id)

    # Filter by completion status
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Filter by priority
    if priority:
        query = query.where(Task.priority == priority)

    # Filter by tags (uses junction table)
    if tag_ids:
        query = query.join(TaskTag).where(TaskTag.tag_id.in_(tag_ids))

    # Search in title and description
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
            )
        )

    # Order by created_at descending
    query = query.order_by(Task.created_at.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks
```

**Example: Tag Autocomplete**:

```python
async def autocomplete_tags(
    session: AsyncSession,
    user_id: str,
    query: str,
    limit: int = 10,
) -> list[Tag]:
    """Get tag suggestions using indexed LIKE query"""

    stmt = (
        select(Tag)
        .where(
            and_(
                Tag.user_id == user_id,
                Tag.name.ilike(f"{query}%"),  # Uses text_pattern_ops index
            )
        )
        .limit(limit)
    )

    result = await session.execute(stmt)
    tags = result.scalars().all()

    return tags
```

**Example: Get Task with Tags (Eager Loading)**:

```python
from sqlalchemy.orm import selectinload


async def get_task_with_tags(
    session: AsyncSession,
    task_id: int,
    user_id: str,
) -> Optional[Task]:
    """Get task with tags loaded (eager loading)"""

    stmt = (
        select(Task)
        .where(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
            )
        )
        .options(
            selectinload(Task.task_tags).selectinload(TaskTag.tag)
        )
    )

    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    return task
```

### 9. Create Model Validation

**Example: Custom Validation**:

```python
from pydantic import validator


class Task(SQLModel, table=True):
    # ... (previous fields)

    @validator("title")
    def title_must_not_be_empty(cls, v):
        """Ensure title is not empty or only whitespace"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @validator("priority")
    def priority_must_be_valid(cls, v):
        """Ensure priority is one of the allowed values"""
        if v not in [PriorityEnum.HIGH, PriorityEnum.MEDIUM, PriorityEnum.LOW]:
            raise ValueError("Priority must be high, medium, or low")
        return v
```

### 10. Database Indexes Summary

**All Indexes Created**:

```python
# Tasks table indexes
# 1. Primary key: tasks.id (automatic)
# 2. Foreign key: tasks.user_id (explicit)
# 3. Search/sort: tasks.title (explicit)
# 4. Filter: tasks.completed (explicit)
# 5. Filter/sort: tasks.priority (explicit)
# 6. Sort: tasks.created_at (explicit)
# 7. Composite: (user_id, completed) for filtered queries
# 8. Composite: (user_id, priority) for filtered queries
# 9. Composite: (user_id, created_at DESC) for sorted queries

# Tags table indexes
# 1. Primary key: tags.id (automatic)
# 2. Foreign key: tags.user_id (explicit)
# 3. Autocomplete: tags.name with text_pattern_ops (explicit)
# 4. Unique: (user_id, name) for constraint (explicit)

# TaskTag junction table indexes
# 1. Composite primary key: (task_id, tag_id) (automatic)
# 2. Lookup: task_tags.task_id (explicit)
# 3. Lookup: task_tags.tag_id (explicit)

# User table indexes
# 1. Primary key: user.id (automatic)
# 2. Unique: user.email (explicit)
```

### 11. Performance Optimization Tips

**Query Performance**:

```python
# ✅ GOOD: Uses indexes
query = select(Task).where(
    and_(
        Task.user_id == user_id,  # Uses idx_tasks_user_completed
        Task.completed == False,
    )
)

# ❌ BAD: No index on description
query = select(Task).where(
    Task.description.contains("important")  # Full table scan
)

# ✅ GOOD: Full-text search (add GIN index for better performance)
# Add to migrations: CREATE INDEX idx_tasks_description_gin ON tasks USING GIN (to_tsvector('english', description));
```

**Lazy vs Eager Loading**:

```python
# ❌ BAD: N+1 query problem
tasks = await session.execute(select(Task))
for task in tasks.scalars():
    tags = task.task_tags  # Separate query for each task!

# ✅ GOOD: Eager loading
tasks = await session.execute(
    select(Task).options(
        selectinload(Task.task_tags).selectinload(TaskTag.tag)
    )
)
```

## Best Practices

1. **Always Use Indexes**: Add indexes on foreign keys and frequently queried fields
2. **Composite Indexes**: Create composite indexes for common query patterns
3. **Timestamps**: Include created_at and updated_at for audit trail
4. **Cascade Deletes**: Use ondelete="CASCADE" for dependent records
5. **Unique Constraints**: Prevent duplicate data with unique indexes
6. **Type Safety**: Use Enums for fixed value sets
7. **Nullable Fields**: Use Optional[] for nullable columns
8. **Max Length**: Always specify max_length for strings
9. **Foreign Keys**: Always index foreign key columns
10. **Validation**: Add Pydantic validators for business logic

## Common Patterns

### One-to-Many Relationship
```python
# Parent (One)
class User(SQLModel, table=True):
    tasks: list["Task"] = Relationship(back_populates="user")

# Child (Many)
class Task(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="tasks")
```

### Many-to-Many Relationship
```python
# Junction table
class TaskTag(SQLModel, table=True):
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
```

### Soft Delete Pattern
```python
class Task(SQLModel, table=True):
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
```

## Success Criteria

- ✅ All models have table=True
- ✅ Foreign keys defined with proper types
- ✅ Indexes added on frequently queried fields
- ✅ Composite indexes for common query patterns
- ✅ created_at and updated_at timestamps included
- ✅ Enums used for fixed value sets
- ✅ Relationships defined with back_populates
- ✅ Cascade delete configured where appropriate
- ✅ Unique constraints enforced
- ✅ Models validated with Pydantic validators

## Troubleshooting

### Issue: Foreign key constraint fails
**Solution**: Ensure referenced table exists first, check cascade settings

### Issue: Index not being used
**Solution**: Check query pattern matches index definition, use EXPLAIN ANALYZE

### Issue: Relationship not loading
**Solution**: Use selectinload() for eager loading, check back_populates

### Issue: Unique constraint violation
**Solution**: Check for existing records before insert, handle exceptions

## Related Skills

- `fastapi_project_setup`: FastAPI and database setup
- `async_route_handlers`: Using models in async routes
- `database_migrations`: Managing schema changes

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/20/core/)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [Pydantic Validators](https://docs.pydantic.dev/latest/usage/validators/)
