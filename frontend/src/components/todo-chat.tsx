'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { sendMessage } from '../lib/api/chat';
import { useAuth } from '../lib/context/auth';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface TodoChatProps {
  onTaskOperation?: () => void; // Callback to trigger task refresh when AI processes task operations
}

const TodoChat: React.FC<TodoChatProps> = ({ onTaskOperation }) => {
  const router = useRouter();
  const { user, loading, verifyUser } = useAuth();
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Scroll to bottom of messages when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim()) return;

    // Get token from localStorage and use actual user ID from auth context
    const token = localStorage.getItem('auth_token');

    // Add user message to the chat
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send message to backend API using actual user ID if available
      const response = await sendMessage(
        inputMessage,
        user?.id?.toString() || "guest",  // Use actual user ID if logged in, otherwise guest
        token || "",                     // Use token if available
        conversationId || undefined      // Pass conversation ID if we have one
      );

      // Save the conversation ID from the response (first message sets it)
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add AI response to the chat
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);

      // Check if the response indicates a task operation was performed
      // Trigger task refresh if task-related keywords are detected in the response
      const responseText = response.response.toLowerCase();
      if (responseText.includes('task') &&
          (responseText.includes('added') ||
           responseText.includes('deleted') ||
           responseText.includes('completed') ||
           responseText.includes('updated') ||
           responseText.includes('created'))) {
        // Call the callback to trigger a task list refresh after a short delay
        setTimeout(() => {
          if (onTaskOperation) {
            onTaskOperation();
          }
        }, 500); // Small delay to ensure the response is fully processed
      }
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to the chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Show login prompt if user is not authenticated
  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4">
        <h3 className="text-lg font-medium mb-2">Please Log In</h3>
        <p className="text-gray-600 mb-4">You need to be logged in to use the chat feature</p>
        <button
          onClick={() => router.push('/login')}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md"
        >
          Login
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-white rounded-lg shadow-md overflow-hidden">
      {/* Chat Header */}
      <div className="bg-gray-100 p-4 border-b">
        <h2 className="text-xl font-semibold text-gray-800">Todo AI Assistant</h2>
        <p className="text-sm text-gray-600">Manage your tasks with AI assistance</p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 max-h-[500px]">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-4">
            <div className="mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-700">Welcome to Todo AI Assistant!</h3>
            <p className="text-gray-600 mt-1">
              I can help you manage your tasks. Try asking me to add, list, complete, or delete tasks.
            </p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-left">
              <div className="bg-blue-50 p-3 rounded-md">
                <p className="font-medium text-blue-800">Examples:</p>
                <ul className="list-disc list-inside mt-1 text-blue-700">
                  <li>Add "Buy groceries" to my tasks</li>
                  <li>Show me my tasks</li>
                </ul>
              </div>
              <div className="bg-green-50 p-3 rounded-md">
                <p className="font-medium text-green-800">&nbsp;</p>
                <ul className="list-disc list-inside mt-1 text-green-700">
                  <li>Complete task #1</li>
                  <li>Delete task "Buy groceries"</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-500'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 rounded-lg px-4 py-2 max-w-[80%]">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce delay-75"></div>
                <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="border-t bg-white p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Ask me to add, list, complete, or delete tasks
        </p>
      </form>
    </div>
  );
};

export default TodoChat;