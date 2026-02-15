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
  user: {
    id: number;
    email: string;
  };
}

interface User {
  id: number;
  email: string;
  created_at: string;
  is_active: boolean;
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
      // Handle case where response might not be JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      } else {
        // If it's not JSON, return a generic error
        const errorText = await response.text();
        throw new Error(`Registration failed: ${response.status} ${response.statusText}. Details: ${errorText}`);
      }
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
      // Handle case where response might not be JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      } else {
        // If it's not JSON, return a generic error
        const errorText = await response.text();
        throw new Error(`Login failed: ${response.status} ${response.statusText}. Details: ${errorText}`);
      }
    }

    return response.json();
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  isAuthenticated(): boolean {
    // Check if there's a token in localStorage
    const token = localStorage.getItem('auth_token');
    return !!token;
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
    } finally {
      // Always clear the auth token from localStorage
      localStorage.removeItem('auth_token');
    }
  }
}

export const authAPI = new AuthAPI();