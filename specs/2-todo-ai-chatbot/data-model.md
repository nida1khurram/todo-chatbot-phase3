# Todo AI Chatbot Data Model

## Overview
This document describes the extended data model for the Todo AI Chatbot feature, building upon the existing Todo application schema.

## Entity Relationships
```
User (1) <---> (Many) Task
User (1) <---> (Many) Conversation
Conversation (1) <---> (Many) Message
```

## Entity Definitions

### User (Existing)
- **Fields**:
  - `id`: integer, primary key
  - `email`: string, unique, required
  - `hashed_password`: string, required
  - `created_at`: datetime, default now
  - `updated_at`: datetime, default now

- **Relationships**:
  - `tasks`: List of Task objects
  - `conversations`: List of Conversation objects
  - `messages`: List of Message objects

### Task (Extended)
- **Fields**:
  - `id`: integer, primary key
  - `user_id`: integer, foreign key to User.id, required
  - `title`: string, required, max_length=255
  - `description`: text, optional
  - `completed`: boolean, default false
  - `created_at`: datetime, default now
  - `updated_at`: datetime, default now

- **Validation**:
  - Title must be 1-255 characters
  - User must exist
  - User can only access their own tasks

- **Relationships**:
  - `user`: User object (owner of the task)

### Conversation (New)
- **Fields**:
  - `id`: integer, primary key
  - `user_id`: integer, foreign key to User.id, required
  - `created_at`: datetime, default now
  - `updated_at`: datetime, default now

- **Validation**:
  - User must exist
  - User can only access their own conversations

- **Relationships**:
  - `user`: User object (owner of the conversation)
  - `messages`: List of Message objects

### Message (New)
- **Fields**:
  - `id`: integer, primary key
  - `user_id`: integer, foreign key to User.id, required
  - `conversation_id`: integer, foreign key to Conversation.id, required
  - `role`: string, required, enum: ["user", "assistant"]
  - `content`: text, required
  - `created_at`: datetime, default now

- **Validation**:
  - Content must be 1-10000 characters
  - Role must be either "user" or "assistant"
  - Conversation must exist
  - User must own the conversation
  - User can only access their own messages

- **Relationships**:
  - `user`: User object (sender of the message)
  - `conversation`: Conversation object (parent conversation)

## Indexes

### Required Indexes
1. `idx_task_user_id` on Task.user_id for efficient user task queries
2. `idx_conversation_user_id` on Conversation.user_id for efficient user conversation queries
3. `idx_message_conversation_id` on Message.conversation_id for efficient conversation message queries
4. `idx_message_user_id` on Message.user_id for efficient user message queries
5. `idx_message_created_at` on Message.created_at DESC for chronological message ordering

## Constraints

### Foreign Key Constraints
1. Task.user_id → User.id
2. Conversation.user_id → User.id
3. Message.user_id → User.id
4. Message.conversation_id → Conversation.id

### Unique Constraints
1. None (multiple conversations and messages allowed per user)

## Access Control Rules

### User Isolation
1. Users can only access their own tasks
2. Users can only access their own conversations
3. Users can only access their own messages
4. Admin users (if any) can access all records

### Validation Checks
1. When querying tasks, filter by user_id
2. When querying conversations, filter by user_id
3. When querying messages, filter by user_id or conversation_id with user ownership check
4. When creating records, ensure user_id matches authenticated user

## State Transitions

### Task State Transitions
- `incomplete` → `completed` (when marked as complete)
- `completed` → `incomplete` (when marked as incomplete)

### Message State
- Messages are immutable after creation
- Only the associated conversation can be modified

## Data Lifecycle

### Task Lifecycle
1. Created with completed=false
2. May transition to completed=true
3. May transition back to completed=false
4. Deleted when user removes it
5. Automatically purged after retention period (TBD)

### Conversation Lifecycle
1. Created when user starts first chat
2. Messages added during chat session
3. Remains active until user ends session or timeout
4. Archived after period of inactivity
5. Purged after retention period (TBD)

### Message Lifecycle
1. Created when user sends message
2. AI response generated and stored
3. Associated with conversation
4. Immutable after creation
5. Purged when conversation is deleted

## Performance Considerations

### Query Optimization
1. Limit message history to last N messages in UI
2. Paginate long conversations
3. Cache frequently accessed conversation metadata
4. Batch operations when possible

### Storage Optimization
1. Compress long message content if needed
2. Archive old conversations to cold storage
3. Implement soft deletes initially