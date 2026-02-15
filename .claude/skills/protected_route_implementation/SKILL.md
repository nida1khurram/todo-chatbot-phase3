# Protected Route Implementation Skill

## Description
Protect API routes by adding get_current_user dependency, verify user_id in URL matches authenticated user_id from token, filter all database queries by user_id, and return 403 for unauthorized access.

## When to Use
- Implementing user isolation in API endpoints
- Protecting routes with authentication
- Preventing users from accessing other users' data
- Enforcing authorization rules
- Securing CRUD operations with user ownership

## Prerequisites
- FastAPI project set up
- JWT verification middleware implemented
- Database models with user_id foreign key
- SQLModel/SQLAlchemy configured
- Understanding of FastAPI dependencies

## Core Concepts

### User Isolation
- Every resource belongs to a user (user_id foreign key)
- Users can only access their own resources
- All queries filtered by authenticated user_id
- Prevents unauthorized data access

### Authentication vs Authorization
- **Authentication**: Who are you? (JWT verification)
- **Authorization**: What can you do? (User isolation)

### Defense in Depth
- Layer 1: JWT token verification
- Layer 2: User ID validation
- Layer 3: Query-level filtering
- Layer 4: Response verification

## Skill Steps

### 1. Create Current User Dependency

**middleware/auth.py** (enhanced):

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.settings import settings
from core.database import get_session
from models import User

# HTTP Bearer security scheme
security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT Bearer token authentication",
    auto_error=False,
)


def extract_token_from_header(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Extract JWT token from Authorization header"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Expected Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id_from_token(token: str = Depends(extract_token_from_header)) -> str:
    """
    Extract user_id from JWT token.

    Returns:
        User ID string from token payload

    Raises:
        HTTPException: 401 if token invalid or user_id missing
    """
    payload = verify_jwt_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user_id (sub claim)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user(
    user_id: str = Depends(get_user_id_from_token),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Get current authenticated user from database.

    Verifies user exists in database.

    Args:
        user_id: User ID from JWT token
        session: Database session

    Returns:
        User model instance

    Raises:
        HTTPException: 401 if user not found

    Example:
        @router.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
    """
    from sqlalchemy import select

    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Token may be invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def verify_user_access(
    path_user_id: str,
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify that authenticated user matches user_id in URL path.

    Enforces user isolation: users can only access their own resources.

    Args:
        path_user_id: User ID from URL path parameter
        current_user: Current authenticated user

    Returns:
        Current user if verification succeeds

    Raises:
        HTTPException: 403 if user_ids don't match

    Example:
        @router.get("/{user_id}/tasks")
        async def get_tasks(
            user_id: str,
            current_user: User = Depends(verify_user_access),
        ):
            # user_id verified to match authenticated user
            pass
    """
    if path_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource",
        )

    return current_user
```

### 2. Protected Route Patterns

**Pattern 1: Simple Protection (user_id from token)**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_session
from middleware.auth import get_user_id_from_token
from models import Task
from schemas.task import TaskResponse

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str = Depends(get_user_id_from_token),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all tasks for authenticated user.

    Security:
    - JWT token required (get_user_id_from_token)
    - User can only see their own tasks
    """
    # Query filtered by authenticated user_id
    result = await session.execute(
        select(Task).where(Task.user_id == user_id)
    )
    tasks = result.scalars().all()

    return tasks
```

**Pattern 2: Protection with User Model**

```python
from middleware.auth import get_current_user
from models import User


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's profile.

    Security:
    - JWT token required
    - User verified to exist in database
    """
    return current_user
```

**Pattern 3: Protection with Path Verification**

```python
from middleware.auth import verify_user_access


@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    current_user: User = Depends(verify_user_access),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all tasks for user.

    Security:
    - JWT token required
    - Path user_id must match authenticated user
    - Returns 403 if trying to access another user's tasks
    """
    result = await session.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    tasks = result.scalars().all()

    return tasks
```

### 3. Complete Protected Routes Example

**routes/tasks.py** (fully protected):

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Optional

from core.database import get_session
from middleware.auth import get_current_user
from models import Task, TaskTag, Tag, User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """
    List all tasks for authenticated user.

    Security: JWT required, user isolation enforced
    """
    # Base query filtered by user
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply filters
    if status_filter and status_filter != "all":
        query = query.where(
            Task.completed == (status_filter == "completed")
        )

    if priority:
        priorities = priority.split(",")
        query = query.where(Task.priority.in_(priorities))

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
            )
        )

    # Execute query
    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a single task by ID.

    Security:
    - JWT required
    - Task must belong to authenticated user
    - Returns 404 if task doesn't exist or belongs to another user
    """
    result = await session.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,  # User isolation
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


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task.

    Security:
    - JWT required
    - Task automatically assigned to authenticated user
    - User cannot create tasks for other users
    """
    # Create task for authenticated user only
    task = Task(
        user_id=current_user.id,  # Force authenticated user_id
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
    )

    session.add(task)
    await session.flush()

    # Handle tag associations
    if task_data.tag_ids:
        # Verify tags belong to current user
        result = await session.execute(
            select(Tag).where(
                and_(
                    Tag.id.in_(task_data.tag_ids),
                    Tag.user_id == current_user.id,  # User isolation
                )
            )
        )
        tags = result.scalars().all()

        if len(tags) != len(task_data.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tag IDs are invalid or don't belong to you",
            )

        # Create associations
        for tag_id in task_data.tag_ids:
            task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
            session.add(task_tag)

    await session.commit()
    await session.refresh(task)

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a task.

    Security:
    - JWT required
    - Task must belong to authenticated user
    - User cannot update other users' tasks
    """
    # Get task with user isolation
    result = await session.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "tag_ids":
            continue
        setattr(task, field, value)

    # Update tags if provided
    if "tag_ids" in update_data:
        # Verify tags belong to current user
        if update_data["tag_ids"]:
            result = await session.execute(
                select(Tag).where(
                    and_(
                        Tag.id.in_(update_data["tag_ids"]),
                        Tag.user_id == current_user.id,
                    )
                )
            )
            tags = result.scalars().all()

            if len(tags) != len(update_data["tag_ids"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more tag IDs are invalid or don't belong to you",
                )

        # Remove existing associations
        await session.execute(
            TaskTag.__table__.delete().where(TaskTag.task_id == task_id)
        )

        # Add new associations
        if update_data["tag_ids"]:
            for tag_id in update_data["tag_ids"]:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)

    await session.commit()
    await session.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a task.

    Security:
    - JWT required
    - Task must belong to authenticated user
    - User cannot delete other users' tasks
    """
    result = await session.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    await session.delete(task)
    await session.commit()

    return None


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Toggle task completion status.

    Security: JWT required, user isolation enforced
    """
    result = await session.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    task.completed = not task.completed

    await session.commit()
    await session.refresh(task)

    return task
```

### 4. Protected Tag Routes

**routes/tags.py**:

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from core.database import get_session
from middleware.auth import get_current_user
from models import Tag, TaskTag, User
from schemas.tag import TagCreate, TagResponse, TagWithCount

router = APIRouter()


@router.get("/", response_model=list[TagResponse])
async def get_tags(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all tags for authenticated user.

    Security: JWT required, user isolation enforced
    """
    result = await session.execute(
        select(Tag).where(Tag.user_id == current_user.id)
    )
    tags = result.scalars().all()

    return tags


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new tag.

    Security:
    - JWT required
    - Tag automatically assigned to authenticated user
    - Check for duplicate tag names per user
    """
    # Check if tag name already exists for this user
    result = await session.execute(
        select(Tag).where(
            and_(
                Tag.user_id == current_user.id,
                Tag.name == tag_data.name.lower(),
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag '{tag_data.name}' already exists",
        )

    # Create tag
    tag = Tag(
        user_id=current_user.id,
        name=tag_data.name.lower(),
    )

    session.add(tag)
    await session.commit()
    await session.refresh(tag)

    return tag


@router.get("/autocomplete", response_model=list[TagResponse])
async def autocomplete_tags(
    query: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get tag autocomplete suggestions.

    Security: JWT required, only searches user's own tags
    """
    result = await session.execute(
        select(Tag)
        .where(
            and_(
                Tag.user_id == current_user.id,
                Tag.name.ilike(f"{query}%"),
            )
        )
        .limit(limit)
    )
    tags = result.scalars().all()

    return tags


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a tag.

    Security: JWT required, user can only delete their own tags
    """
    result = await session.execute(
        select(Tag).where(
            and_(
                Tag.id == tag_id,
                Tag.user_id == current_user.id,
            )
        )
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    await session.delete(tag)
    await session.commit()

    return None


@router.get("/stats", response_model=list[TagWithCount])
async def get_tag_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get tags with task counts.

    Security: JWT required, only counts user's own tasks
    """
    result = await session.execute(
        select(
            Tag,
            func.count(TaskTag.task_id).label("task_count"),
        )
        .outerjoin(TaskTag, Tag.id == TaskTag.tag_id)
        .where(Tag.user_id == current_user.id)
        .group_by(Tag.id)
    )

    tags_with_counts = []
    for tag, count in result.all():
        tag_dict = {
            "id": tag.id,
            "user_id": tag.user_id,
            "name": tag.name,
            "created_at": tag.created_at,
            "task_count": count,
        }
        tags_with_counts.append(tag_dict)

    return tags_with_counts
```

### 5. Security Testing

**Test User Isolation**:

```python
# tests/test_security.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cannot_access_other_user_tasks(client: AsyncClient):
    """Test that user cannot access another user's tasks"""

    # User 1 creates a task
    user1_token = "user1_jwt_token"
    response = await client.post(
        "/api/user1/tasks",
        json={"title": "User 1 Task", "priority": "medium"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    task_id = response.json()["id"]

    # User 2 tries to access User 1's task
    user2_token = "user2_jwt_token"
    response = await client.get(
        f"/api/user1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )

    # Should return 404 (not 403 to avoid information leakage)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_update_other_user_tasks(client: AsyncClient):
    """Test that user cannot update another user's tasks"""

    user1_token = "user1_jwt_token"
    user2_token = "user2_jwt_token"

    # User 1 creates a task
    response = await client.post(
        "/api/user1/tasks",
        json={"title": "User 1 Task", "priority": "medium"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    task_id = response.json()["id"]

    # User 2 tries to update User 1's task
    response = await client.patch(
        f"/api/user2/tasks/{task_id}",
        json={"title": "Hacked!"},
        headers={"Authorization": f"Bearer {user2_token}"},
    )

    # Should return 404
    assert response.status_code == 404
```

### 6. Common Security Pitfalls

**❌ BAD: Using path user_id without verification**

```python
@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,  # From URL - not verified!
    session: AsyncSession = Depends(get_session),
):
    # VULNERABLE: Any user can access any user's tasks
    result = await session.execute(
        select(Task).where(Task.user_id == user_id)
    )
    return result.scalars().all()
```

**✅ GOOD: Always use authenticated user_id**

```python
@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,  # From URL
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # SECURE: Use authenticated user_id from token
    result = await session.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    return result.scalars().all()
```

**❌ BAD: Accepting user_id in request body**

```python
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str,  # From request body - DANGEROUS!
    session: AsyncSession = Depends(get_session),
):
    # VULNERABLE: User can create tasks for other users
    task = Task(user_id=user_id, **task_data.dict())
    # ...
```

**✅ GOOD: Force authenticated user_id**

```python
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # SECURE: Use authenticated user_id
    task = Task(user_id=current_user.id, **task_data.dict())
    # ...
```

### 7. Response Sanitization

**Ensure no data leakage in error messages**:

```python
# ❌ BAD: Leaks information
if not task:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="This task belongs to another user",  # Info leak!
    )

# ✅ GOOD: Generic message
if not task:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found",  # Could be missing or belongs to another user
    )
```

## Best Practices

1. **Always Filter by user_id**: Every query must filter by authenticated user_id
2. **Use Dependencies**: Leverage FastAPI dependencies for consistent security
3. **Return 404, Not 403**: Don't reveal if resource exists for another user
4. **Verify Relationships**: Check that related resources (tags) belong to user
5. **Force user_id**: Never accept user_id from request body or path parameter
6. **Test User Isolation**: Write tests to verify users can't access others' data
7. **Audit Logging**: Log access attempts for security monitoring
8. **Defense in Depth**: Multiple layers of security checks
9. **No Information Leakage**: Generic error messages
10. **Document Security**: Add security notes to endpoint docstrings

## Common Patterns

### Pattern: Get with User Isolation
```python
result = await session.execute(
    select(Task).where(
        and_(
            Task.id == task_id,
            Task.user_id == current_user.id,
        )
    )
)
```

### Pattern: Create with Forced user_id
```python
task = Task(
    user_id=current_user.id,  # From token, not request
    **task_data.dict()
)
```

### Pattern: Update with Ownership Check
```python
# 1. Get resource with user filter
task = await get_task_or_404(task_id, current_user.id)

# 2. Update resource
task.title = new_title

# 3. Save
await session.commit()
```

## Success Criteria

- ✅ All routes protected with authentication dependency
- ✅ user_id from token used, never from path/body
- ✅ All queries filtered by authenticated user_id
- ✅ 403 returned for unauthorized access attempts
- ✅ Related resources verified to belong to user
- ✅ No information leakage in error messages
- ✅ User isolation tested with integration tests
- ✅ Security documented in endpoint docstrings
- ✅ Consistent security patterns across all routes
- ✅ No direct use of path/body user_id in queries

## Troubleshooting

### Issue: User can access another user's data
**Solution**: Always filter queries by current_user.id from token, not path parameter

### Issue: User can create resources for other users
**Solution**: Force user_id=current_user.id in create operations

### Issue: Related resources not verified
**Solution**: Check that tags/categories belong to user before associating

### Issue: Error messages leak information
**Solution**: Return generic 404 instead of 403

## Related Skills

- `jwt_verification`: Token verification
- `restful_api_design`: API endpoint design
- `database_connection_setup`: Database session management

## References

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
