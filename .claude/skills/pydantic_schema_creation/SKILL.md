# Pydantic Schema Creation Skill

## Description
Create separate Pydantic schemas for Create, Update, and Response operations, add Field validation with min/max constraints, implement optional fields for updates, and ensure proper type hints throughout.

## When to Use
- Creating request/response schemas for FastAPI endpoints
- Separating data validation from database models
- Implementing different validation rules for Create vs Update
- Adding custom validation logic with validators
- Ensuring type safety across API boundaries

## Prerequisites
- FastAPI project set up
- Pydantic 2.x installed
- SQLModel models defined
- Understanding of Pydantic validation
- TypeScript-like type hints knowledge

## Core Concepts

### Schema Separation Pattern
- **Base Schema**: Shared fields between Create and Response
- **Create Schema**: Required fields for creating new records
- **Update Schema**: Optional fields for partial updates
- **Response Schema**: Fields returned to client (includes DB fields)

### Pydantic Field Validation
- `Field()` for constraints and metadata
- `min_length`, `max_length` for strings
- `ge`, `le`, `gt`, `lt` for numbers
- `pattern` for regex validation
- `default` and `default_factory` for defaults
- Custom validators with `@validator` or `@field_validator`

### Type Hints
- `str`, `int`, `bool`, `float` for basic types
- `Optional[T]` for nullable fields
- `list[T]` for arrays
- `dict[K, V]` for objects
- `datetime` for timestamps
- `EmailStr` for email validation

## Skill Steps

### 1. Create User Schemas

**schemas/user.py**:

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Base user schema with shared fields.
    Used as foundation for other schemas.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name",
        examples=["John Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["john.doe@example.com"],
    )


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    All fields are required.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User's password (minimum 8 characters)",
        examples=["SecurePassword123!"],
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name is not just whitespace"""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User's full name",
    )
    email: Optional[EmailStr] = Field(
        None,
        description="User's email address",
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure name is not just whitespace if provided"""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip() if v else v


class UserResponse(UserBase):
    """
    Schema for user response.
    Includes database-generated fields.
    """
    id: str = Field(
        ...,
        description="User's unique identifier",
        examples=["user_123abc"],
    )
    email_verified: bool = Field(
        default=False,
        description="Whether the user's email is verified",
    )
    created_at: datetime = Field(
        ...,
        description="When the user was created",
    )
    updated_at: datetime = Field(
        ...,
        description="When the user was last updated",
    )

    class Config:
        from_attributes = True  # Pydantic 2.x (was orm_mode in v1)
        json_schema_extra = {
            "example": {
                "id": "user_123abc",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "email_verified": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class SignInRequest(BaseModel):
    """Schema for sign-in request"""
    email: EmailStr = Field(
        ...,
        description="User's email address",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User's password",
    )


class AuthResponse(BaseModel):
    """Schema for authentication response"""
    user: UserResponse = Field(
        ...,
        description="Authenticated user information",
    )
    token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
```

### 2. Create Task Schemas

**schemas/task.py**:

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum


class PriorityEnum(str, Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TagInTask(BaseModel):
    """Nested tag schema for task response"""
    id: int = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """Base task schema with shared fields"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title",
        examples=["Complete project documentation"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Task description",
        examples=["Write comprehensive API documentation"],
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        description="Task priority level",
        examples=["high"],
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace"""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        """Trim description whitespace"""
        return v.strip() if v else v


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    All base fields are required.
    """
    tag_ids: Optional[list[int]] = Field(
        None,
        description="List of tag IDs to associate with the task",
        examples=[[1, 2, 3]],
    )

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, v: Optional[list[int]]) -> Optional[list[int]]:
        """Validate tag IDs are unique and positive"""
        if v is not None:
            if len(v) != len(set(v)):
                raise ValueError("Tag IDs must be unique")
            if any(tag_id <= 0 for tag_id in v):
                raise ValueError("Tag IDs must be positive integers")
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating a task.
    All fields are optional for partial updates.
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Task title",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Task description",
    )
    priority: Optional[PriorityEnum] = Field(
        None,
        description="Task priority level",
    )
    completed: Optional[bool] = Field(
        None,
        description="Task completion status",
    )
    tag_ids: Optional[list[int]] = Field(
        None,
        description="List of tag IDs to associate with the task",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not just whitespace if provided"""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v else v

    @field_validator("description")
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        """Trim description whitespace"""
        return v.strip() if v else v

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, v: Optional[list[int]]) -> Optional[list[int]]:
        """Validate tag IDs are unique and positive"""
        if v is not None:
            if len(v) != len(set(v)):
                raise ValueError("Tag IDs must be unique")
            if any(tag_id <= 0 for tag_id in v):
                raise ValueError("Tag IDs must be positive integers")
        return v


class TaskResponse(TaskBase):
    """
    Schema for task response.
    Includes database-generated fields and relationships.
    """
    id: int = Field(
        ...,
        description="Task ID",
        examples=[1],
    )
    user_id: str = Field(
        ...,
        description="User ID who owns the task",
        examples=["user_123abc"],
    )
    completed: bool = Field(
        default=False,
        description="Task completion status",
    )
    created_at: datetime = Field(
        ...,
        description="When the task was created",
    )
    updated_at: datetime = Field(
        ...,
        description="When the task was last updated",
    )
    tags: list[TagInTask] = Field(
        default=[],
        description="Tags associated with the task",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123abc",
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation",
                "completed": False,
                "priority": "high",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "tags": [
                    {"id": 1, "name": "work"},
                    {"id": 2, "name": "documentation"},
                ],
            }
        }


class TaskListResponse(BaseModel):
    """Schema for paginated task list response"""
    tasks: list[TaskResponse] = Field(
        ...,
        description="List of tasks",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of tasks",
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of tasks per page",
    )
```

### 3. Create Tag Schemas

**schemas/tag.py**:

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class TagBase(BaseModel):
    """Base tag schema with shared fields"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Tag name",
        examples=["work"],
    )

    @field_validator("name")
    @classmethod
    def name_lowercase(cls, v: str) -> str:
        """Convert tag name to lowercase and trim whitespace"""
        return v.strip().lower()

    @field_validator("name")
    @classmethod
    def name_alphanumeric(cls, v: str) -> str:
        """Ensure tag name contains only alphanumeric characters, hyphens, and underscores"""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Tag name must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v


class TagCreate(TagBase):
    """
    Schema for creating a new tag.
    All fields are required.
    """
    pass


class TagUpdate(BaseModel):
    """
    Schema for updating a tag.
    All fields are optional.
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Tag name",
    )

    @field_validator("name")
    @classmethod
    def name_lowercase(cls, v: Optional[str]) -> Optional[str]:
        """Convert tag name to lowercase and trim whitespace"""
        return v.strip().lower() if v else v

    @field_validator("name")
    @classmethod
    def name_alphanumeric(cls, v: Optional[str]) -> Optional[str]:
        """Ensure tag name contains only alphanumeric characters, hyphens, and underscores"""
        if v is not None and not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Tag name must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v


class TagResponse(TagBase):
    """
    Schema for tag response.
    Includes database-generated fields.
    """
    id: int = Field(
        ...,
        description="Tag ID",
        examples=[1],
    )
    user_id: str = Field(
        ...,
        description="User ID who owns the tag",
        examples=["user_123abc"],
    )
    created_at: datetime = Field(
        ...,
        description="When the tag was created",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123abc",
                "name": "work",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class TagWithCount(TagResponse):
    """Tag response with task count"""
    task_count: int = Field(
        ...,
        ge=0,
        description="Number of tasks with this tag",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123abc",
                "name": "work",
                "created_at": "2024-01-01T00:00:00Z",
                "task_count": 5,
            }
        }
```

### 4. Create Common/Shared Schemas

**schemas/common.py**:

```python
from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar
from datetime import datetime


T = TypeVar("T")


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")


class ErrorDetail(BaseModel):
    """Error detail schema"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = Field(False, description="Operation success status")
    message: str = Field(..., description="Error message")
    errors: Optional[list[ErrorDetail]] = Field(
        None,
        description="Detailed error information",
    )


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = Field(
        1,
        ge=1,
        description="Page number (1-indexed)",
    )
    page_size: int = Field(
        20,
        ge=1,
        le=100,
        description="Number of items per page",
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    @property
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
```

### 5. Create Query Parameter Schemas

**schemas/query_params.py**:

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class StatusFilter(str, Enum):
    """Task status filter options"""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class SortBy(str, Enum):
    """Sort by options"""
    CREATED_AT = "created_at"
    PRIORITY = "priority"
    TITLE = "title"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class TaskQueryParams(BaseModel):
    """Query parameters for task listing"""
    status: StatusFilter = Field(
        StatusFilter.ALL,
        description="Filter by status",
    )
    priority: Optional[str] = Field(
        None,
        pattern="^(high|medium|low)(,(high|medium|low))*$",
        description="Filter by priority (comma-separated)",
        examples=["high,medium"],
    )
    tags: Optional[str] = Field(
        None,
        pattern="^[0-9]+(,[0-9]+)*$",
        description="Filter by tag IDs (comma-separated)",
        examples=["1,2,3"],
    )
    search: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Search in title and description",
    )
    sort_by: SortBy = Field(
        SortBy.CREATED_AT,
        description="Sort by field",
    )
    sort_order: SortOrder = Field(
        SortOrder.DESC,
        description="Sort order",
    )
    page: int = Field(
        1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        20,
        ge=1,
        le=100,
        description="Items per page",
    )

    def get_priority_list(self) -> Optional[list[str]]:
        """Parse comma-separated priority string to list"""
        if self.priority:
            return self.priority.split(",")
        return None

    def get_tag_ids(self) -> Optional[list[int]]:
        """Parse comma-separated tag IDs to list of integers"""
        if self.tags:
            return [int(tag_id) for tag_id in self.tags.split(",")]
        return None


class TagAutocompleteParams(BaseModel):
    """Query parameters for tag autocomplete"""
    query: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Search query",
    )
    limit: int = Field(
        10,
        ge=1,
        le=50,
        description="Maximum number of results",
    )
```

### 6. Update schemas/__init__.py

**schemas/__init__.py**:

```python
"""API schemas package"""

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    SignInRequest,
    AuthResponse,
)

# Task schemas
from .task import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    PriorityEnum,
    TagInTask,
)

# Tag schemas
from .tag import (
    TagBase,
    TagCreate,
    TagUpdate,
    TagResponse,
    TagWithCount,
)

# Common schemas
from .common import (
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
    PaginationParams,
    PaginatedResponse,
    TimestampMixin,
)

# Query parameters
from .query_params import (
    TaskQueryParams,
    TagAutocompleteParams,
    StatusFilter,
    SortBy,
    SortOrder,
)


__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "SignInRequest",
    "AuthResponse",
    # Task
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "PriorityEnum",
    "TagInTask",
    # Tag
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagWithCount",
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "ErrorDetail",
    "PaginationParams",
    "PaginatedResponse",
    "TimestampMixin",
    # Query params
    "TaskQueryParams",
    "TagAutocompleteParams",
    "StatusFilter",
    "SortBy",
    "SortOrder",
]
```

### 7. Using Schemas in Routes

**Example: Task Route with Schemas**:

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from schemas.query_params import TaskQueryParams
from typing import Annotated

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,  # Request body validated by Pydantic
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task.

    - **title**: Task title (1-200 characters)
    - **description**: Optional description (max 1000 characters)
    - **priority**: Priority level (high, medium, low)
    - **tag_ids**: Optional list of tag IDs
    """
    # task_data is already validated by Pydantic
    # Access fields: task_data.title, task_data.priority, etc.

    # Create task in database
    # ...

    return task_response  # Automatically serialized to TaskResponse


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    params: Annotated[TaskQueryParams, Query()],  # Query params validated
    session: AsyncSession = Depends(get_session),
):
    """
    Get all tasks with filters.

    Query parameters are validated by TaskQueryParams schema.
    """
    # Access validated params
    priority_list = params.get_priority_list()
    tag_ids = params.get_tag_ids()

    # Query database
    # ...

    return tasks  # List automatically serialized to list[TaskResponse]


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,  # Partial update schema
    session: AsyncSession = Depends(get_session),
):
    """
    Update a task.

    All fields are optional - only provided fields will be updated.
    """
    # Get only fields that were actually provided
    update_data = task_data.model_dump(exclude_unset=True)

    # Update task in database with only provided fields
    # ...

    return updated_task
```

### 8. Custom Validators

**Advanced Validation Examples**:

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    @field_validator("due_date")
    @classmethod
    def due_date_in_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure due date is in the future"""
        if v is not None and v < datetime.utcnow():
            raise ValueError("Due date must be in the future")
        return v

    @model_validator(mode="after")
    def check_dates(self) -> "TaskCreate":
        """Ensure start_date is before due_date"""
        if self.start_date and self.due_date:
            if self.start_date > self.due_date:
                raise ValueError("Start date must be before due date")
        return self
```

## Best Practices

1. **Separation of Concerns**: Keep Create, Update, and Response schemas separate
2. **Optional Updates**: All fields in Update schemas should be Optional
3. **Validation**: Add Field constraints and custom validators
4. **Type Hints**: Always use proper type hints for IDE support
5. **Examples**: Provide examples in Field() for documentation
6. **from_attributes**: Use Config.from_attributes = True for ORM models
7. **Enums**: Use Enum for fixed value sets
8. **Nested Schemas**: Create separate schemas for nested objects
9. **Reusable Base**: Use Base schemas for shared fields
10. **Documentation**: Add docstrings and descriptions

## Common Patterns

### Base + Inheritance Pattern
```python
class TaskBase(BaseModel):
    title: str
    priority: str

class TaskCreate(TaskBase):
    pass  # Inherits all fields as required

class TaskUpdate(BaseModel):
    title: Optional[str] = None  # All optional
    priority: Optional[str] = None
```

### Nested Schema Pattern
```python
class TagInTask(BaseModel):
    id: int
    name: str

class TaskResponse(BaseModel):
    id: int
    title: str
    tags: list[TagInTask] = []  # Nested schema
```

### Partial Update Pattern
```python
@router.put("/{id}")
async def update(data: UpdateSchema):
    # Only update provided fields
    update_data = data.model_dump(exclude_unset=True)
    # Apply update_data to model
```

## Success Criteria

- ✅ Separate schemas for Create, Update, and Response
- ✅ Field validation with min/max constraints
- ✅ Optional fields in Update schemas
- ✅ Proper type hints throughout (str, int, Optional, list, etc.)
- ✅ Custom validators for business logic
- ✅ from_attributes = True in Response schemas
- ✅ Enums for fixed value sets
- ✅ Nested schemas for relationships
- ✅ Examples and descriptions in Field()
- ✅ Reusable base schemas for shared fields

## Troubleshooting

### Issue: Validation error not clear
**Solution**: Add descriptive error messages in custom validators

### Issue: ORM model not serializing
**Solution**: Add `from_attributes = True` in Config

### Issue: Optional fields required in update
**Solution**: Ensure all Update schema fields use Optional[]

### Issue: Nested objects not validating
**Solution**: Create separate schema for nested objects

## Related Skills

- `fastapi_project_setup`: FastAPI setup with Pydantic
- `sqlmodel_schema_design`: Database models
- `api_route_handlers`: Using schemas in routes

## References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/usage/validators/)
- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
