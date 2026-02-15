# Data Model: Todo Full-Stack Web Application with Authentication

## Entity: User

**Purpose**: Represents a registered user in the system with authentication credentials

**Fields**:
- `id` (Integer): Primary key, auto-incrementing user identifier
- `email` (String): User's email address, unique, required for authentication
- `password_hash` (String): Securely hashed password using industry-standard algorithm
- `created_at` (DateTime): Timestamp when the user account was created
- `updated_at` (DateTime): Timestamp when the user account was last updated
- `is_active` (Boolean): Flag indicating if the user account is active (default: true)

**Validation Rules**:
- Email must be a valid email format
- Email must be unique across all users
- Password must meet minimum security requirements (handled by authentication system)
- Email cannot be empty

## Entity: Task

**Purpose**: Represents a todo item created by a specific user

**Fields**:
- `id` (Integer): Primary key, auto-incrementing task identifier
- `user_id` (Integer): Foreign key linking to the User who owns this task
- `title` (String): The main text of the task, required
- `description` (String): Optional detailed description of the task
- `completed` (Boolean): Flag indicating if the task is completed (default: false)
- `created_at` (DateTime): Timestamp when the task was created
- `updated_at` (DateTime): Timestamp when the task was last updated
- `due_date` (DateTime): Optional deadline for the task

**Relationships**:
- One User to Many Tasks (user_id foreign key creates the relationship)

**Validation Rules**:
- Title cannot be empty or only whitespace
- User_id must reference an existing, active user
- Task must belong to the authenticated user making the request
- Due date must be in the future if provided

## Entity: Session (Implicit via Better Auth)

**Purpose**: Represents an active user session (handled by Better Auth)

**Fields** (as managed by Better Auth):
- `session_token` (String): Unique identifier for the session
- `user_id` (Integer): Reference to the associated user
- `expires_at` (DateTime): Expiration timestamp for the session
- `created_at` (DateTime): When the session was created

## State Transitions

### Task State Transitions
- **Created**: When a new task is added by a user (completed = false)
- **Completed**: When a user marks a task as complete (completed = true)
- **Reopened**: When a user reopens a completed task (completed = false)
- **Deleted**: When a user deletes a task (record removed from database)

### User State Transitions
- **Registered**: When a user first creates an account (is_active = true)
- **Deactivated**: When a user account is deactivated (is_active = false)
- **Deleted**: When a user account is permanently removed (handled by authentication system)

## Database Constraints

- **Foreign Key Constraint**: Task.user_id references User.id
- **Unique Constraint**: User.email must be unique
- **Not Null Constraints**: Required fields (id, email, title) cannot be null
- **Check Constraints**: Validation rules for data integrity
- **Indexing**: Indexes on user_id for efficient user-specific queries, email for authentication lookups

## Security Considerations

- **Data Isolation**: All task queries must be filtered by user_id to prevent cross-user access
- **Authentication**: Access to user and task data requires valid JWT token
- **Password Security**: Passwords stored only as secure hashes, never in plain text
- **Session Management**: Automatic session handling via Better Auth with secure tokens