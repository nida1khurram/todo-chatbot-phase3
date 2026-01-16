# JWT Verification Skill

## Description
Implement JWT token verification middleware in FastAPI that extracts Bearer token from Authorization header, verifies signature using shared secret, decodes payload to get user_id, and raises HTTPException for invalid tokens.

## When to Use
- Protecting FastAPI endpoints with JWT authentication
- Verifying JWT tokens from Better Auth frontend
- Extracting user_id from authenticated requests
- Implementing authentication middleware
- Securing API routes with Bearer token verification

## Prerequisites
- FastAPI project set up
- python-jose[cryptography] installed
- JWT_SECRET configured in environment variables
- Better Auth configured on frontend
- Understanding of JWT structure (header.payload.signature)

## Core Concepts

### JWT Structure
- **Header**: Algorithm and token type (HS256, JWT)
- **Payload**: Claims (user_id, exp, iat, etc.)
- **Signature**: HMAC signature using secret key

### JWT Verification Process
1. Extract token from Authorization header
2. Verify token signature with secret key
3. Check token expiration
4. Decode payload to get claims
5. Return user_id or raise exception

### Bearer Token Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Skill Steps

### 1. Install JWT Dependencies

**requirements.txt** (add if not present):

```txt
# JWT Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

**Install**:

```bash
cd backend
pip install python-jose[cryptography] passlib[bcrypt]
```

### 2. Update Environment Variables

**.env**:

```bash
# JWT Configuration (must match frontend)
JWT_SECRET=your-jwt-secret-key-min-32-chars-long-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
```

**.env.example**:

```bash
# JWT Configuration
JWT_SECRET=generate-a-secure-random-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. Update Settings Configuration

**core/config/settings.py** (add JWT settings):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Todo API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str
    database_echo: bool = False

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080  # 7 days

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
```

### 4. Create JWT Verification Middleware

**middleware/auth.py**:

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime

from core.config.settings import settings

# HTTP Bearer security scheme
security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT Bearer token authentication",
    auto_error=False,  # Don't auto-raise exception, we'll handle it
)


class JWTVerificationError(Exception):
    """Custom exception for JWT verification errors"""

    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def extract_token_from_header(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """
    Extract JWT token from Authorization header.

    Expected format: Authorization: Bearer <token>

    Args:
        credentials: HTTP authorization credentials from header

    Returns:
        JWT token string

    Raises:
        HTTPException: If Authorization header is missing or malformed
    """
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
    """
    Verify JWT token signature and decode payload.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload (dict with user_id, exp, iat, etc.)

    Raises:
        JWTVerificationError: If token is invalid, expired, or malformed
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        # Check if token has expired
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp)
            if datetime.utcnow() > exp_datetime:
                raise JWTVerificationError(
                    "Token has expired",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

        return payload

    except jwt.ExpiredSignatureError:
        raise JWTVerificationError(
            "Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    except jwt.JWTClaimsError as e:
        raise JWTVerificationError(
            f"Invalid token claims: {str(e)}",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    except JWTError as e:
        raise JWTVerificationError(
            f"Invalid token: {str(e)}",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    except Exception as e:
        raise JWTVerificationError(
            f"Token verification failed: {str(e)}",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


def get_user_id_from_token(token: str = Depends(extract_token_from_header)) -> str:
    """
    Extract user_id from verified JWT token.

    This is the main dependency to use in protected routes.

    Args:
        token: JWT token string (automatically extracted from header)

    Returns:
        User ID string

    Raises:
        HTTPException: If token is invalid or user_id is missing

    Example:
        @router.get("/tasks")
        async def get_tasks(user_id: str = Depends(get_user_id_from_token)):
            # user_id is automatically extracted from JWT token
            pass
    """
    try:
        # Verify token and get payload
        payload = verify_jwt_token(token)

        # Extract user_id from payload
        # Better Auth JWT plugin uses "sub" (subject) claim for user_id
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing user_id (sub claim)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTVerificationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}",
        )


def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """
    Extract user_id from JWT token if present, otherwise return None.

    Use for endpoints that work with or without authentication.

    Args:
        credentials: HTTP authorization credentials from header

    Returns:
        User ID string if authenticated, None otherwise

    Example:
        @router.get("/tasks")
        async def get_tasks(user_id: Optional[str] = Depends(get_optional_user_id)):
            if user_id:
                # Return user-specific tasks
            else:
                # Return public tasks
            pass
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_jwt_token(token)
        return payload.get("sub")

    except (JWTVerificationError, Exception):
        # If token is invalid, treat as unauthenticated
        return None


async def verify_user_matches_path(
    path_user_id: str,
    token_user_id: str = Depends(get_user_id_from_token),
) -> str:
    """
    Verify that user_id in JWT token matches user_id in URL path.

    Use this to enforce user isolation (users can only access their own resources).

    Args:
        path_user_id: User ID from URL path parameter
        token_user_id: User ID from JWT token (automatically verified)

    Returns:
        User ID if verification succeeds

    Raises:
        HTTPException: If user_ids don't match (403 Forbidden)

    Example:
        @router.get("/{user_id}/tasks")
        async def get_tasks(
            user_id: str = Depends(verify_user_matches_path),
            session: AsyncSession = Depends(get_session),
        ):
            # user_id is verified to match JWT token
            pass
    """
    if path_user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource",
        )

    return token_user_id


def get_token_payload(token: str = Depends(extract_token_from_header)) -> dict:
    """
    Get full decoded token payload.

    Use when you need access to additional claims beyond user_id.

    Args:
        token: JWT token string (automatically extracted from header)

    Returns:
        Full decoded token payload

    Raises:
        HTTPException: If token is invalid

    Example:
        @router.get("/profile")
        async def get_profile(payload: dict = Depends(get_token_payload)):
            user_id = payload.get("sub")
            email = payload.get("email")
            roles = payload.get("roles", [])
            # Use additional claims
            pass
    """
    try:
        return verify_jwt_token(token)

    except JWTVerificationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 5. Using JWT Verification in Routes

**routes/tasks.py** (updated with authentication):

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from core.database import get_session
from middleware.auth import get_user_id_from_token, verify_user_matches_path
from models import Task
from schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


# Method 1: Extract user_id from token, ignore path parameter
@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="List all tasks for authenticated user",
)
async def get_tasks(
    user_id: str = Depends(get_user_id_from_token),  # From JWT token
    session: AsyncSession = Depends(get_session),
):
    """
    Get all tasks for authenticated user.

    User ID is automatically extracted from JWT token.
    Path parameter user_id is ignored (for URL consistency).
    """
    result = await session.execute(
        select(Task).where(Task.user_id == user_id)
    )
    tasks = result.scalars().all()

    return tasks


# Method 2: Verify path user_id matches token user_id
@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_user_id_from_token),  # From JWT token
    session: AsyncSession = Depends(get_session),
):
    """
    Get a single task by ID.

    Automatically verifies the task belongs to the authenticated user.
    """
    result = await session.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,  # User isolation enforced
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


# Method 3: Create resource for authenticated user
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_user_id_from_token),  # From JWT token
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task for authenticated user.

    User ID is automatically extracted from JWT token.
    """
    # Create task with authenticated user_id
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


# Method 4: Update with user isolation
@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: str = Depends(get_user_id_from_token),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a task.

    Automatically verifies the task belongs to the authenticated user.
    """
    # Get task with user isolation check
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

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)

    return task


# Method 5: Delete with user isolation
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_user_id_from_token),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a task.

    Automatically verifies the task belongs to the authenticated user.
    """
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

    await session.delete(task)
    await session.commit()

    return None
```

### 6. Optional Authentication Example

**routes/public.py**:

```python
from fastapi import APIRouter, Depends
from typing import Optional

from middleware.auth import get_optional_user_id

router = APIRouter()


@router.get("/stats")
async def get_stats(user_id: Optional[str] = Depends(get_optional_user_id)):
    """
    Get statistics.

    Returns personalized stats if authenticated, public stats otherwise.
    """
    if user_id:
        return {
            "message": f"Personal stats for user {user_id}",
            "type": "personal",
        }
    else:
        return {
            "message": "Public statistics",
            "type": "public",
        }
```

### 7. Testing JWT Verification

**Test with cURL**:

```bash
# 1. Get JWT token from Better Auth (sign in first)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Test protected endpoint with token
curl -X GET "http://localhost:8000/api/user123/tasks" \
  -H "Authorization: Bearer $TOKEN"

# 3. Test without token (should return 401)
curl -X GET "http://localhost:8000/api/user123/tasks"

# 4. Test with invalid token (should return 401)
curl -X GET "http://localhost:8000/api/user123/tasks" \
  -H "Authorization: Bearer invalid_token"

# 5. Create task with authentication
curl -X POST "http://localhost:8000/api/user123/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Test Description",
    "priority": "medium"
  }'
```

### 8. Error Response Examples

**401 Unauthorized - Missing Token**:

```json
{
  "detail": "Authorization header is missing"
}
```

**401 Unauthorized - Invalid Token**:

```json
{
  "detail": "Invalid token: Signature verification failed"
}
```

**401 Unauthorized - Expired Token**:

```json
{
  "detail": "Token has expired"
}
```

**403 Forbidden - User Mismatch**:

```json
{
  "detail": "You don't have permission to access this resource"
}
```

### 9. Custom Exception Handler

**main.py** (add exception handlers):

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from jose import JWTError

@app.exception_handler(JWTError)
async def jwt_error_handler(request: Request, exc: JWTError):
    """Handle JWT verification errors"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Invalid authentication credentials",
            "error": str(exc),
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
```

### 10. Token Debugging Utility

**scripts/debug_token.py**:

```python
#!/usr/bin/env python3
"""
Debug JWT token - decode without verification to inspect payload.
Useful for debugging token issues.

Usage: python debug_token.py <token>
"""

import sys
from jose import jwt

if len(sys.argv) < 2:
    print("Usage: python debug_token.py <token>")
    sys.exit(1)

token = sys.argv[1]

try:
    # Decode without verification to inspect payload
    payload = jwt.get_unverified_claims(token)

    print("Token Payload:")
    print("=" * 50)
    for key, value in payload.items():
        print(f"{key}: {value}")

    # Check expiration
    if "exp" in payload:
        from datetime import datetime
        exp_datetime = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()

        print("\nExpiration Info:")
        print(f"Expires at: {exp_datetime}")
        print(f"Current time: {now}")
        print(f"Expired: {now > exp_datetime}")

except Exception as e:
    print(f"Error decoding token: {e}")
    sys.exit(1)
```

**Usage**:

```bash
python scripts/debug_token.py "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 11. Integration with FastAPI Docs

FastAPI automatically adds authentication to OpenAPI docs when using HTTPBearer:

```python
# The security scheme is automatically added to OpenAPI spec
# Users can click "Authorize" button in /docs
# Enter: Bearer <token>
```

### 12. Rate Limiting (Optional)

**middleware/rate_limit.py**:

```python
from fastapi import HTTPException, status, Request
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

# Simple in-memory rate limiter (use Redis in production)
request_counts: Dict[str, list] = defaultdict(list)

RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds


async def rate_limit_by_token(request: Request, user_id: str) -> None:
    """
    Rate limit by user_id (from JWT token).

    Args:
        request: FastAPI request object
        user_id: User ID from JWT token

    Raises:
        HTTPException: If rate limit exceeded
    """
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    # Clean old requests
    request_counts[user_id] = [
        req_time for req_time in request_counts[user_id]
        if req_time > window_start
    ]

    # Check rate limit
    if len(request_counts[user_id]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds",
        )

    # Record this request
    request_counts[user_id].append(now)
```

## Best Practices

1. **Use HTTPS**: Always use HTTPS in production to protect tokens in transit
2. **Secure Secret**: Use strong random secret key (min 32 characters)
3. **Token Expiration**: Set appropriate expiration time (7 days default)
4. **User Isolation**: Always verify user_id in token matches resource ownership
5. **Error Messages**: Don't leak sensitive info in error messages
6. **Token Refresh**: Implement token refresh for long-lived sessions
7. **Rate Limiting**: Add rate limiting to prevent abuse
8. **Logging**: Log authentication failures for security monitoring
9. **CORS**: Configure CORS properly for frontend domains
10. **Token Revocation**: Consider token blacklist for logout/security

## Common Patterns

### Protected Route Pattern
```python
@router.get("/tasks")
async def get_tasks(
    user_id: str = Depends(get_user_id_from_token),
    session: AsyncSession = Depends(get_session),
):
    # user_id automatically extracted from JWT
    pass
```

### User Isolation Pattern
```python
# Always verify resource belongs to user
result = await session.execute(
    select(Task).where(
        and_(
            Task.id == task_id,
            Task.user_id == user_id,  # From JWT token
        )
    )
)
```

### Optional Auth Pattern
```python
@router.get("/public")
async def public_endpoint(
    user_id: Optional[str] = Depends(get_optional_user_id),
):
    if user_id:
        # Personalized response
    else:
        # Public response
```

## Success Criteria

- ✅ JWT token extracted from Authorization header
- ✅ Bearer token scheme enforced
- ✅ Token signature verified with shared secret
- ✅ Token expiration checked
- ✅ user_id extracted from token payload
- ✅ HTTPException raised for invalid tokens
- ✅ User isolation enforced in routes
- ✅ Protected endpoints working
- ✅ OpenAPI docs show authentication
- ✅ Error handling for all token issues

## Troubleshooting

### Issue: Token signature verification failed
**Solution**: Ensure JWT_SECRET matches between frontend Better Auth and backend

### Issue: Token always returns 401
**Solution**: Check token format (Bearer prefix), verify secret key, check expiration

### Issue: User can access other user's resources
**Solution**: Always filter queries by user_id from token, not path parameter

### Issue: CORS errors with Authorization header
**Solution**: Ensure "Authorization" is in CORS_ALLOW_HEADERS

## Related Skills

- `fastapi_project_setup`: FastAPI setup
- `better_auth_setup`: Frontend JWT generation
- `restful_api_design`: Using auth in REST endpoints

## References

- [JWT.io](https://jwt.io/) - JWT debugger and documentation
- [python-jose Documentation](https://python-jose.readthedocs.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [RFC 7519 - JWT Standard](https://tools.ietf.org/html/rfc7519)
- [RFC 6750 - Bearer Token Usage](https://tools.ietf.org/html/rfc6750)
