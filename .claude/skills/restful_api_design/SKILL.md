# RESTful API Design Skill

## Description
Design RESTful API endpoints following conventions with GET for listing, POST for creating, PUT for full updates, PATCH for partial updates, DELETE for removing, and proper use of HTTP status codes.

## When to Use
- Designing API endpoints for FastAPI application
- Implementing CRUD operations with proper HTTP methods
- Creating consistent API structure
- Choosing appropriate HTTP status codes
- Following REST architectural constraints

## Prerequisites
- FastAPI project set up
- Understanding of HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Understanding of HTTP status codes
- Database models and schemas defined
- RESTful API principles knowledge

## Core Concepts

### REST Principles
- **Resource-Based**: URLs represent resources (nouns, not verbs)
- **HTTP Methods**: Use standard methods for operations
- **Stateless**: Each request contains all information needed
- **Uniform Interface**: Consistent endpoint structure
- **Client-Server**: Separation of concerns

### HTTP Methods
- **GET**: Retrieve resources (safe, idempotent)
- **POST**: Create new resources (not idempotent)
- **PUT**: Replace entire resource (idempotent)
- **PATCH**: Partially update resource (idempotent)
- **DELETE**: Remove resource (idempotent)

### HTTP Status Codes
- **2xx Success**: 200 OK, 201 Created, 204 No Content
- **3xx Redirection**: 301 Moved Permanently, 304 Not Modified
- **4xx Client Errors**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict
- **5xx Server Errors**: 500 Internal Server Error, 503 Service Unavailable

## Skill Steps

### 1. Resource Naming Conventions

**Good REST Endpoint Names**:

```python
# ✅ GOOD: Resource-based, plural nouns
GET    /api/{user_id}/tasks           # List all tasks
GET    /api/{user_id}/tasks/{task_id} # Get specific task
POST   /api/{user_id}/tasks           # Create new task
PUT    /api/{user_id}/tasks/{task_id} # Replace entire task
PATCH  /api/{user_id}/tasks/{task_id} # Update specific fields
DELETE /api/{user_id}/tasks/{task_id} # Delete task

GET    /api/{user_id}/tags            # List all tags
POST   /api/{user_id}/tags            # Create new tag

# ✅ GOOD: Sub-resources
GET    /api/{user_id}/tasks/{task_id}/tags  # Get tags for task

# ✅ GOOD: Actions as sub-resources (when necessary)
PATCH  /api/{user_id}/tasks/{task_id}/complete  # Toggle completion
```

**Bad REST Endpoint Names**:

```python
# ❌ BAD: Verbs in URL
GET    /api/getTasks
POST   /api/createTask
DELETE /api/deleteTask

# ❌ BAD: Inconsistent naming
GET    /api/task          # Singular
GET    /api/alltasks      # No separation
GET    /api/Tasks         # Capitalized

# ❌ BAD: Operation in URL
POST   /api/tasks/create
GET    /api/tasks/list
```

### 2. Complete CRUD Endpoint Implementation

**routes/tasks.py**:

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Optional

from core.database import get_session
from models import Task, TaskTag, Tag
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from schemas.common import SuccessResponse

router = APIRouter()


# ==================== GET: List Resources ====================

@router.get(
    "/",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks",
    description="Retrieve all tasks for the authenticated user with optional filtering and sorting",
)
async def get_tasks(
    user_id: str,
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status: all, pending, completed",
        regex="^(all|pending|completed)$",
    ),
    priority: Optional[str] = Query(
        None,
        description="Filter by priority (comma-separated): high,medium,low",
        regex="^(high|medium|low)(,(high|medium|low))*$",
    ),
    tags: Optional[str] = Query(
        None,
        description="Filter by tag IDs (comma-separated): 1,2,3",
        regex="^[0-9]+(,[0-9]+)*$",
    ),
    search: Optional[str] = Query(
        None,
        min_length=1,
        max_length=100,
        description="Search in title and description",
    ),
    sort_by: Optional[str] = Query(
        "created_at",
        description="Sort by field",
        regex="^(created_at|priority|title)$",
    ),
    sort_order: Optional[str] = Query(
        "desc",
        description="Sort order",
        regex="^(asc|desc)$",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session),
):
    """
    List all tasks for user.

    Query Parameters:
    - status: Filter by completion status
    - priority: Filter by priority levels
    - tags: Filter by tag IDs
    - search: Search in title and description
    - sort_by: Sort by field (created_at, priority, title)
    - sort_order: Sort direction (asc, desc)
    - page: Page number for pagination
    - page_size: Number of items per page

    Returns:
    - 200 OK: List of tasks
    """
    try:
        # Build query
        query = select(Task).where(Task.user_id == user_id)

        # Filter by status
        if status_filter and status_filter != "all":
            query = query.where(
                Task.completed == (status_filter == "completed")
            )

        # Filter by priority
        if priority:
            priorities = priority.split(",")
            query = query.where(Task.priority.in_(priorities))

        # Filter by tags
        if tags:
            tag_ids = [int(tid) for tid in tags.split(",")]
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

        # Apply sorting
        if sort_by == "created_at":
            sort_column = Task.created_at
        elif sort_by == "priority":
            sort_column = Task.priority
        elif sort_by == "title":
            sort_column = Task.title
        else:
            sort_column = Task.created_at

        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await session.execute(query)
        tasks = result.scalars().all()

        return tasks

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}",
        )


# ==================== GET: Single Resource ====================

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
    description="Retrieve a single task by its ID",
)
async def get_task(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a single task by ID.

    Path Parameters:
    - task_id: Task ID to retrieve

    Returns:
    - 200 OK: Task found
    - 404 Not Found: Task does not exist
    - 403 Forbidden: Task belongs to different user
    """
    try:
        # Query task
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == user_id,
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        return task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task: {str(e)}",
        )


# ==================== POST: Create Resource ====================

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user",
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task.

    Request Body:
    - title: Task title (required, 1-200 characters)
    - description: Task description (optional, max 1000 characters)
    - priority: Priority level (required: high, medium, low)
    - tag_ids: List of tag IDs to associate (optional)

    Returns:
    - 201 Created: Task created successfully
    - 400 Bad Request: Invalid input data
    - 409 Conflict: Duplicate task or invalid tag IDs
    """
    try:
        # Create task
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
        )

        session.add(task)
        await session.flush()  # Get task.id without committing

        # Associate tags if provided
        if task_data.tag_ids:
            # Verify tags exist and belong to user
            result = await session.execute(
                select(Tag).where(
                    and_(
                        Tag.id.in_(task_data.tag_ids),
                        Tag.user_id == user_id,
                    )
                )
            )
            tags = result.scalars().all()

            if len(tags) != len(task_data.tag_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more tag IDs are invalid",
                )

            # Create task-tag associations
            for tag_id in task_data.tag_ids:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)

        await session.commit()
        await session.refresh(task)

        return task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}",
        )


# ==================== PUT: Full Update ====================

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Replace a task",
    description="Replace entire task (all fields required)",
)
async def replace_task(
    user_id: str,
    task_id: int,
    task_data: TaskCreate,  # All fields required for PUT
    session: AsyncSession = Depends(get_session),
):
    """
    Replace entire task (PUT replaces the complete resource).

    All fields must be provided, even if unchanged.

    Path Parameters:
    - task_id: Task ID to replace

    Request Body:
    - All fields from TaskCreate schema (required)

    Returns:
    - 200 OK: Task replaced successfully
    - 404 Not Found: Task does not exist
    - 400 Bad Request: Invalid input data
    """
    try:
        # Get existing task
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == user_id,
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Replace all fields
        task.title = task_data.title
        task.description = task_data.description
        task.priority = task_data.priority
        # completed status is reset to False in full replacement
        task.completed = False

        # Replace tags
        # Remove existing tag associations
        await session.execute(
            TaskTag.__table__.delete().where(TaskTag.task_id == task_id)
        )

        # Add new tag associations
        if task_data.tag_ids:
            for tag_id in task_data.tag_ids:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)

        await session.commit()
        await session.refresh(task)

        return task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to replace task: {str(e)}",
        )


# ==================== PATCH: Partial Update ====================

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Partially update task (only provided fields are updated)",
)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,  # All fields optional for PATCH
    session: AsyncSession = Depends(get_session),
):
    """
    Partially update task (PATCH updates only provided fields).

    Only fields included in the request body will be updated.

    Path Parameters:
    - task_id: Task ID to update

    Request Body:
    - Any fields from TaskUpdate schema (all optional)

    Returns:
    - 200 OK: Task updated successfully
    - 404 Not Found: Task does not exist
    - 400 Bad Request: Invalid input data
    """
    try:
        # Get existing task
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == user_id,
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Get only fields that were provided (exclude_unset=True)
        update_data = task_data.model_dump(exclude_unset=True)

        # Update only provided fields
        for field, value in update_data.items():
            if field == "tag_ids":
                # Handle tag associations separately
                continue
            setattr(task, field, value)

        # Update tags if provided
        if "tag_ids" in update_data:
            # Remove existing tag associations
            await session.execute(
                TaskTag.__table__.delete().where(TaskTag.task_id == task_id)
            )

            # Add new tag associations
            if update_data["tag_ids"]:
                for tag_id in update_data["tag_ids"]:
                    task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                    session.add(task_tag)

        await session.commit()
        await session.refresh(task)

        return task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}",
        )


# ==================== DELETE: Remove Resource ====================

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task",
)
async def delete_task(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a task.

    Path Parameters:
    - task_id: Task ID to delete

    Returns:
    - 204 No Content: Task deleted successfully
    - 404 Not Found: Task does not exist
    """
    try:
        # Get existing task
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == user_id,
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Delete task (cascade will delete task_tags)
        await session.delete(task)
        await session.commit()

        # 204 No Content has no response body
        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}",
        )


# ==================== PATCH: Action on Resource ====================

@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion",
    description="Toggle the completion status of a task",
)
async def toggle_task_complete(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Toggle task completion status.

    This is an action endpoint using PATCH.

    Path Parameters:
    - task_id: Task ID to toggle

    Returns:
    - 200 OK: Task completion toggled
    - 404 Not Found: Task does not exist
    """
    try:
        # Get existing task
        result = await session.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == user_id,
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Toggle completion
        task.completed = not task.completed

        await session.commit()
        await session.refresh(task)

        return task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle task completion: {str(e)}",
        )
```

### 3. HTTP Status Codes Reference

**Success Status Codes**:

```python
from fastapi import status

# 200 OK - Standard success response
@router.get("/tasks")
async def get_tasks():
    return tasks  # status.HTTP_200_OK (default)

# 201 Created - Resource created successfully
@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task():
    return new_task

# 204 No Content - Success with no response body
@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task():
    return None  # No response body

# 202 Accepted - Request accepted but not yet processed
@router.post("/tasks/bulk", status_code=status.HTTP_202_ACCEPTED)
async def bulk_create():
    return {"message": "Bulk operation queued"}
```

**Client Error Status Codes**:

```python
# 400 Bad Request - Invalid request data
if not data.title:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Title is required",
    )

# 401 Unauthorized - Authentication required
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required",
    headers={"WWW-Authenticate": "Bearer"},
)

# 403 Forbidden - Authenticated but not authorized
if task.user_id != current_user_id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this task",
    )

# 404 Not Found - Resource doesn't exist
if not task:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with id {task_id} not found",
    )

# 409 Conflict - Duplicate or conflict with current state
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="A task with this title already exists",
)

# 422 Unprocessable Entity - Validation error (FastAPI default)
# Automatically returned by FastAPI for Pydantic validation errors

# 429 Too Many Requests - Rate limit exceeded
raise HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Rate limit exceeded. Try again later.",
)
```

**Server Error Status Codes**:

```python
# 500 Internal Server Error - Unexpected server error
try:
    result = await dangerous_operation()
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"An unexpected error occurred: {str(e)}",
    )

# 503 Service Unavailable - Service temporarily unavailable
raise HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Database temporarily unavailable",
)
```

### 4. Nested Resources and Relationships

**Sub-resource Endpoints**:

```python
# Get tags for a specific task
@router.get(
    "/{task_id}/tags",
    response_model=list[TagResponse],
    status_code=status.HTTP_200_OK,
)
async def get_task_tags(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all tags associated with a task"""
    # Verify task exists and belongs to user
    task = await get_task(user_id, task_id, session)

    # Get tags
    result = await session.execute(
        select(Tag)
        .join(TaskTag)
        .where(TaskTag.task_id == task_id)
    )
    tags = result.scalars().all()

    return tags


# Add tag to a task
@router.post(
    "/{task_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def add_tag_to_task(
    user_id: str,
    task_id: int,
    tag_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Associate a tag with a task"""
    # Verify task and tag exist
    task = await get_task(user_id, task_id, session)
    tag = await get_tag(user_id, tag_id, session)

    # Check if association already exists
    result = await session.execute(
        select(TaskTag).where(
            and_(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already associated with task",
        )

    # Create association
    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
    session.add(task_tag)
    await session.commit()

    return None


# Remove tag from task
@router.delete(
    "/{task_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_tag_from_task(
    user_id: str,
    task_id: int,
    tag_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Remove tag association from task"""
    # Delete association
    result = await session.execute(
        TaskTag.__table__.delete().where(
            and_(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id,
            )
        )
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag association not found",
        )

    await session.commit()
    return None
```

### 5. Bulk Operations

**Bulk Create**:

```python
@router.post(
    "/bulk",
    response_model=list[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_tasks(
    user_id: str,
    tasks_data: list[TaskCreate],
    session: AsyncSession = Depends(get_session),
):
    """Create multiple tasks at once"""
    if len(tasks_data) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 tasks per bulk operation",
        )

    tasks = []
    for task_data in tasks_data:
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
        )
        tasks.append(task)

    session.add_all(tasks)
    await session.commit()

    return tasks


# Bulk Delete
@router.delete(
    "/bulk",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def bulk_delete_tasks(
    user_id: str,
    task_ids: list[int],
    session: AsyncSession = Depends(get_session),
):
    """Delete multiple tasks at once"""
    await session.execute(
        Task.__table__.delete().where(
            and_(
                Task.id.in_(task_ids),
                Task.user_id == user_id,
            )
        )
    )
    await session.commit()

    return None
```

### 6. Pagination and Filtering

**Pagination with Headers**:

```python
from fastapi import Response

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    response: Response = None,
    session: AsyncSession = Depends(get_session),
):
    """Get tasks with pagination headers"""

    # Get total count
    count_result = await session.execute(
        select(func.count()).select_from(Task).where(Task.user_id == user_id)
    )
    total = count_result.scalar()

    # Get paginated results
    offset = (page - 1) * page_size
    result = await session.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .offset(offset)
        .limit(page_size)
    )
    tasks = result.scalars().all()

    # Add pagination headers
    total_pages = (total + page_size - 1) // page_size
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Total-Pages"] = str(total_pages)
    response.headers["X-Page"] = str(page)
    response.headers["X-Page-Size"] = str(page_size)

    return tasks
```

## Best Practices

1. **Use Plural Nouns**: `/tasks`, not `/task`
2. **Resource-Based URLs**: Use nouns, not verbs
3. **Consistent Naming**: Use lowercase with hyphens for multi-word resources
4. **Proper HTTP Methods**: GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove)
5. **Correct Status Codes**: 200 (OK), 201 (Created), 204 (No Content), 404 (Not Found), etc.
6. **Idempotency**: GET, PUT, PATCH, DELETE should be idempotent
7. **Versioning**: Use `/api/v1/` prefix for versioning
8. **Filtering**: Use query parameters for filtering, sorting, pagination
9. **Nested Resources**: Use for parent-child relationships
10. **Error Responses**: Consistent error format with detail messages

## Common Patterns

### CRUD Operations Summary
```python
GET    /api/{user_id}/tasks          # List (200)
POST   /api/{user_id}/tasks          # Create (201)
GET    /api/{user_id}/tasks/{id}     # Read (200)
PUT    /api/{user_id}/tasks/{id}     # Replace (200)
PATCH  /api/{user_id}/tasks/{id}     # Update (200)
DELETE /api/{user_id}/tasks/{id}     # Delete (204)
```

### PUT vs PATCH
```python
# PUT: Replace entire resource (all fields required)
PUT /tasks/1
{
  "title": "New Title",
  "description": "New Description",
  "priority": "high"
}

# PATCH: Update specific fields (only provided fields)
PATCH /tasks/1
{
  "title": "New Title"  # Only title is updated
}
```

### Error Response Format
```python
{
  "detail": "Task with id 123 not found",  # FastAPI default
  # Or custom format:
  "success": false,
  "message": "Task not found",
  "errors": [
    {
      "field": "task_id",
      "message": "Task with id 123 not found",
      "type": "not_found"
    }
  ]
}
```

## Success Criteria

- ✅ Resource-based URLs with plural nouns
- ✅ Proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- ✅ Correct HTTP status codes (200, 201, 204, 404, etc.)
- ✅ Consistent endpoint naming conventions
- ✅ Query parameters for filtering and pagination
- ✅ Proper error handling with descriptive messages
- ✅ Idempotent operations (GET, PUT, PATCH, DELETE)
- ✅ Nested resources for relationships
- ✅ Bulk operations for efficiency
- ✅ Complete CRUD implementation

## Troubleshooting

### Issue: Should I use PUT or PATCH?
**Solution**: Use PUT for full replacement (all fields required), PATCH for partial updates (only changed fields)

### Issue: What status code for validation errors?
**Solution**: 422 Unprocessable Entity (FastAPI default for Pydantic validation)

### Issue: Should DELETE return data?
**Solution**: Use 204 No Content with no response body (or 200 OK if returning deleted resource)

### Issue: How to handle sub-resources?
**Solution**: Use nested URLs: `/tasks/{task_id}/tags`

## Related Skills

- `fastapi_project_setup`: FastAPI application setup
- `pydantic_schema_creation`: Request/response schemas
- `sqlmodel_schema_design`: Database models

## References

- [REST API Design Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [FastAPI Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/)
- [Roy Fielding's REST Dissertation](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
