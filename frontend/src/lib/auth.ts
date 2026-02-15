// frontend/src/lib/auth.ts
import { createAuthClient } from 'better-auth/client';

// Create the auth client with the API base URL
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
  // Add any additional configuration here
});

// Export types for authentication
export type { Session, User } from 'better-auth/client';