# OpenAI ChatKit Integration Skill

## Description
Integrate OpenAI ChatKit with your Todo application for conversational AI interface. Creates a seamless chat experience that connects to your AI backend and MCP tools for natural language todo management.

## When to Use This Skill
- Creating conversational interface for todo management
- Integrating with existing authentication system
- Connecting frontend to AI backend services
- Implementing real-time chat functionality
- Building user-friendly AI interaction

## Prerequisites
- OpenAI ChatKit domain allowlisted
- Backend chat API endpoint available
- Authentication system with JWT tokens
- Proper CORS configuration for chat requests
- MCP server and AI agent services running

## Implementation Steps

### 1. Install ChatKit Dependencies
```bash
npm install @openai/chat-components @openai/chatkit-react
# Or yarn equivalent
```

### 2. Configure Domain Allowlist
```javascript
// First, add your domain to OpenAI's allowlist:
// Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
// Click "Add domain" and enter your frontend URL (e.g., https://your-app.vercel.app)
// After adding the domain, OpenAI will provide a domain key
```

### 3. Create Chat Component with Authentication
```typescript
// frontend/src/components/todo-chat.tsx
'use client';

import { Chat, type Message } from '@openai/chat-components';
import { useAuth } from '../lib/context/auth'; // Your existing auth context
import { useEffect, useState } from 'react';

interface TodoChatProps {
  userId: string;
}

export default function TodoChat({ userId }: TodoChatProps) {
  const { token } = useAuth(); // Get JWT token from existing auth
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return <div>Loading chat...</div>;
  }

  const handleCreateMessage = async (input: string) => {
    // Include authentication token in the request
    const response = await fetch(`/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include JWT token
      },
      body: JSON.stringify({
        message: input,
        conversation_id: localStorage.getItem(`chat_conversation_${userId}`) || null
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  };

  return (
    <div className="w-full max-w-4xl h-[600px] border rounded-lg overflow-hidden">
      <Chat
        className="h-full"
        initialMessages={[]}
        messageSettings={{
          assistantName: 'Todo Assistant',
        }}
        displayInputSettings={{
          inputDisabled: false,
          submitButtonDisabled: false,
        }}
        onCreateMessage={handleCreateMessage}
        onRenderFunctionCall={({ name, arguments: args }) => (
          <div className="bg-blue-50 p-3 rounded-md text-sm">
            <div className="font-semibold">{name}</div>
            <pre className="mt-1 text-xs bg-white p-2 rounded border">
              {JSON.stringify(args, null, 2)}
            </pre>
          </div>
        )}
      />
    </div>
  );
}
```

### 4. Create Chat Page with Authentication Protection
```typescript
// frontend/src/app/chat/page.tsx
'use client';

import { useAuth } from '../../lib/context/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import TodoChat from '../../components/todo-chat';
import { Spinner } from '../../components/ui/spinner';

export default function ChatPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      setUserId(user.id.toString());
    }
  }, [user, authLoading, router]);

  if (authLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner />
      </div>
    );
  }

  if (!user) {
    return null; // Redirect handled by useEffect
  }

  if (!userId) {
    return <div>Error: User ID not available</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Todo Chat Assistant</h1>
      <p className="mb-4 text-gray-600">
        Chat with your AI assistant to manage your todos naturally.
      </p>

      <TodoChat userId={userId} />

      <div className="mt-6 text-sm text-gray-500">
        <p>You can say things like:</p>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>"Add a task to buy groceries"</li>
          <li>"Show me all my pending tasks"</li>
          <li>"Mark task 3 as complete"</li>
          <li>"Delete the meeting task"</li>
        </ul>
      </div>
    </div>
  );
}
```

### 5. Update Environment Variables
```bash
# Add to frontend/.env.local
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_from_openai
NEXT_PUBLIC_API_URL=http://localhost:8000  # Your backend URL
```

### 6. Create Chat API Client
```typescript
// frontend/src/lib/api/chat.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ChatMessage {
  message: string;
  conversation_id?: number | null;
}

interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls?: Array<{
    name: string;
    arguments: Record<string, any>;
  }>;
}

class ChatAPI {
  async sendMessage(userId: string, messageData: ChatMessage, token: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(messageData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send message');
    }

    return response.json();
  }
}

export const chatAPI = new ChatAPI();
```

### 7. Update Authentication Context to Support Chat
```typescript
// Update frontend/src/lib/context/auth.tsx to ensure token is available
// The existing auth context should already provide the token needed for the chat
```

## Key Implementation Notes

### Authentication Integration
- Pass JWT token from existing auth system to chat API calls
- Ensure user ID matches between authentication and chat requests
- Handle token expiration and refresh if needed

### Error Handling
- Display user-friendly error messages for chat failures
- Handle network errors gracefully
- Provide fallback messaging when AI is unavailable

### User Experience
- Show loading states during AI processing
- Display tool calls to help users understand AI actions
- Provide usage examples and tips

### Security
- Ensure all chat requests include proper authentication
- Validate user ID matches authenticated user
- Prevent unauthorized access to other users' conversations

## Testing Strategy
```javascript
// frontend/src/__tests__/TodoChat.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TodoChat from '../components/todo-chat';

// Mock the Chat component and auth context
vi.mock('@openai/chat-components', () => ({
  Chat: ({ onCreateMessage, initialMessages }: any) => (
    <div data-testid="chat-component">
      <div>Chat Component</div>
      <button
        onClick={() => onCreateMessage('test message')}
        data-testid="send-message-btn"
      >
        Send
      </button>
    </div>
  ),
}));

vi.mock('../lib/context/auth', () => ({
  useAuth: () => ({
    token: 'mock-jwt-token',
    user: { id: '123' },
  }),
}));

describe('TodoChat', () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ conversation_id: 1, response: 'Hello!' }),
      })
    ) as any;
  });

  it('renders chat component', () => {
    render(<TodoChat userId="123" />);
    expect(screen.getByTestId('chat-component')).toBeInTheDocument();
  });

  it('sends message to backend', async () => {
    render(<TodoChat userId="123" />);

    fireEvent.click(screen.getByTestId('send-message-btn'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/123/chat'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-jwt-token',
          }),
        })
      );
    });
  });
});
```

## Common Issues and Solutions

### Issue: Domain Not Allowlisted
**Problem**: ChatKit doesn't load due to domain restriction
**Solution**: Add your domain to OpenAI's domain allowlist and use the provided domain key

### Issue: Authentication Headers
**Problem**: Chat requests fail due to missing authentication
**Solution**: Ensure JWT token is properly passed in Authorization header

### Issue: CORS Configuration
**Problem**: Cross-origin requests blocked
**Solution**: Configure proper CORS settings in backend to allow frontend origin

### Issue: ChatKit Loading
**Problem**: ChatKit component fails to load
**Solution**: Verify domain key is correct and domain is properly configured

## Success Criteria
- [ ] ChatKit component loads without errors
- [ ] Authentication tokens properly passed to chat API
- [ ] Messages sent and received successfully
- [ ] Tool calls displayed properly in UI
- [ ] User isolation maintained through authentication
- [ ] Error handling works appropriately
- [ ] Responsive design works across devices

## Files Created
- `frontend/src/components/todo-chat.tsx` - Chat component
- `frontend/src/app/chat/page.tsx` - Chat page with auth protection
- `frontend/src/lib/api/chat.ts` - Chat API client
- `frontend/src/__tests__/TodoChat.test.tsx` - Tests (optional)