// frontend/src/lib/api/auth.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface User {
  id: string;
  email: string;
  created_at: string;
}

class AuthAPI {
  async register(data: RegisterData): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Registration failed');
    }

    return response.json();
  }

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    return response.json();
  }

  async logout(): Promise<void> {
    try {
      // Call the backend logout endpoint
      const token = localStorage.getItem('auth_token');
      if (token) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      // Even if the backend call fails, still clear the local token
      console.error('Logout error (ignored):', error);
    } finally {
      // Always clear the auth token from localStorage
      localStorage.removeItem('auth_token');
    }
  }

  isAuthenticated(): boolean {
    // Check if there's a token in localStorage
    const token = localStorage.getItem('auth_token');
    return !!token;
  }

  getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }
}

export const authAPI = new AuthAPI();