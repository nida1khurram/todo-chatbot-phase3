'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import TodoChat from '@/components/todo-chat';
import { LoadingSpinner } from '@/components/loading-spinner';
import { useAuth } from '@/lib/context/auth';

export default function ChatPage() {
  const router = useRouter();
  const { user, loading, verifyUser } = useAuth();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      if (loading) return;

      try {
        const isValid = await verifyUser();
        if (!isValid) {
          router.push('/login');
        } else {
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth verification error:', error);
        // Clear any invalid tokens and redirect to login
        localStorage.removeItem('auth_token');
        router.push('/login');
      } finally {
        setHasCheckedAuth(true);
      }
    };

    checkAuth();
  }, [loading, router, verifyUser]);

  if (loading || !hasCheckedAuth) {
    return (
      <div className="flex justify-center items-center h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Redirecting to login...</p>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Todo AI Assistant</h1>
        <p className="text-gray-600">Chat with our AI assistant to manage your tasks</p>
      </div>

      <div className="h-[600px]">
        <TodoChat />
      </div>
    </div>
  );
}