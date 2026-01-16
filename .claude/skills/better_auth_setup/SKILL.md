# Better Auth Setup Skill

## Description
Configure Better Auth with Neon PostgreSQL database, enable email/password authentication, configure JWT plugin with secret and expiration, set up session management, and create auth API routes.

## When to Use
- Setting up authentication for Next.js frontend
- Implementing email/password authentication
- Configuring JWT tokens for API authorization
- Creating sign-up and sign-in functionality
- Managing user sessions

## Prerequisites
- Next.js 15+ with App Router configured
- Neon PostgreSQL database created
- Better Auth package installed
- Environment variables configured
- Understanding of JWT authentication

## Core Concepts

### Better Auth
- Modern authentication library for Next.js
- Built-in support for multiple providers
- Automatic database schema management
- Session management with JWT
- Type-safe client and server APIs

### Email/Password Authentication
- User registration with email and password
- Password hashing with bcrypt
- Email verification (optional)
- Password reset functionality

### JWT Plugin
- Stateless authentication tokens
- Configurable expiration time
- Secret key for signing tokens
- Token refresh mechanism

## Skill Steps

### 1. Install Better Auth Dependencies

**Install packages**:

```bash
cd frontend

# Install Better Auth and JWT plugin
npm install better-auth @better-auth/jwt

# Install additional dependencies
npm install postgres  # For Neon connection
```

**Update package.json**:

```json
{
  "dependencies": {
    "better-auth": "^1.0.0",
    "@better-auth/jwt": "^1.0.0",
    "postgres": "^3.4.4",
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }
}
```

### 2. Configure Environment Variables

**.env.local**:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-long-change-this-immediately
BETTER_AUTH_URL=http://localhost:3000

# Database Connection (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require

# JWT Configuration
JWT_SECRET=your-jwt-secret-key-min-32-chars-long-change-this
JWT_EXPIRES_IN=7d  # 7 days

# API Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**.env.example**:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=generate-a-secure-random-key-here
BETTER_AUTH_URL=http://localhost:3000

# Database Connection (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require

# JWT Configuration
JWT_SECRET=generate-another-secure-random-key-here
JWT_EXPIRES_IN=7d

# API Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Generate secure keys**:

```bash
# Generate BETTER_AUTH_SECRET
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Generate JWT_SECRET
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 3. Create Better Auth Configuration

**lib/auth/auth.ts**:

```typescript
import { betterAuth } from "better-auth";
import { jwt } from "@better-auth/jwt";
import postgres from "postgres";

// Create Neon PostgreSQL connection
const sql = postgres(process.env.DATABASE_URL!, {
  ssl: "require",
  max: 10,
  idle_timeout: 20,
  connect_timeout: 10,
});

// Better Auth configuration
export const auth = betterAuth({
  // Database connection
  database: sql,

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
    minPasswordLength: 8,
    maxPasswordLength: 100,
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // Cache for 5 minutes
    },
  },

  // Account configuration
  account: {
    accountLinking: {
      enabled: false, // Disable multiple providers for same email
      trustedProviders: [],
    },
  },

  // Base URL for redirects
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",

  // Secret key for encryption
  secret: process.env.BETTER_AUTH_SECRET!,

  // Plugins
  plugins: [
    jwt({
      jwt: {
        secret: process.env.JWT_SECRET!,
        expiresIn: process.env.JWT_EXPIRES_IN || "7d",
      },
    }),
  ],

  // Advanced options
  advanced: {
    generateId: () => {
      // Generate custom user IDs (optional)
      return `user_${Math.random().toString(36).substring(2, 15)}`;
    },
    cookiePrefix: "todo_app",
    crossSubDomainCookies: {
      enabled: false,
    },
  },

  // User schema (optional customization)
  user: {
    additionalFields: {
      // Add custom fields if needed
      // role: {
      //   type: "string",
      //   defaultValue: "user",
      // },
    },
  },
});

// Export types for client usage
export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.User;
```

### 4. Create Auth API Route Handler

**app/api/auth/[...all]/route.ts**:

```typescript
import { auth } from "@/lib/auth/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Export HTTP method handlers
export const { GET, POST } = toNextJsHandler(auth);

// Optional: Configure route segment
export const runtime = "nodejs"; // or "edge"
export const dynamic = "force-dynamic";
```

### 5. Create Client-Side Auth Helper

**lib/auth/client.ts**:

```typescript
"use client";

import { createAuthClient } from "better-auth/client";
import { jwtClient } from "@better-auth/jwt/client";

// Create auth client for client-side usage
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});

// Export auth methods for convenience
export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
  updateUser,
} = authClient;
```

### 6. Create Server-Side Auth Helper

**lib/auth/server.ts**:

```typescript
import { auth } from "./auth";
import { cookies } from "next/headers";
import { cache } from "react";

/**
 * Get current session on server side.
 * Cached to avoid multiple database calls in single request.
 */
export const getServerSession = cache(async () => {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("todo_app.session_token")?.value;

  if (!sessionToken) {
    return null;
  }

  try {
    const session = await auth.api.getSession({
      headers: {
        cookie: `todo_app.session_token=${sessionToken}`,
      },
    });

    return session;
  } catch (error) {
    console.error("Failed to get session:", error);
    return null;
  }
});

/**
 * Get current user on server side.
 */
export const getServerUser = cache(async () => {
  const session = await getServerSession();
  return session?.user || null;
});

/**
 * Require authentication on server side.
 * Throws error if not authenticated.
 */
export const requireAuth = async () => {
  const session = await getServerSession();

  if (!session) {
    throw new Error("Unauthorized");
  }

  return session;
};
```

### 7. Create Sign-Up Page

**app/(auth)/signup/page.tsx**:

```typescript
import { SignUpForm } from "@/components/forms/SignUpForm";
import Link from "next/link";

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{" "}
            <Link
              href="/signin"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Sign in
            </Link>
          </p>
        </div>

        <SignUpForm />
      </div>
    </div>
  );
}
```

**components/forms/SignUpForm.tsx**:

```typescript
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signUp } from "@/lib/auth/client";

export function SignUpForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setIsLoading(true);

    try {
      await signUp.email({
        name,
        email,
        password,
      });

      // Redirect to tasks page on success
      router.push("/tasks");
    } catch (err: any) {
      setError(err.message || "Failed to create account");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-8 space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Full Name
          </label>
          <input
            id="name"
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
          <p className="mt-1 text-sm text-gray-500">
            Must be at least 8 characters
          </p>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            type="password"
            required
            minLength={8}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? "Creating account..." : "Sign up"}
      </button>
    </form>
  );
}
```

### 8. Create Sign-In Page

**app/(auth)/signin/page.tsx**:

```typescript
import { SignInForm } from "@/components/forms/SignInForm";
import Link from "next/link";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Don't have an account?{" "}
            <Link
              href="/signup"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Sign up
            </Link>
          </p>
        </div>

        <SignInForm />
      </div>
    </div>
  );
}
```

**components/forms/SignInForm.tsx**:

```typescript
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signIn } from "@/lib/auth/client";

export function SignInForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await signIn.email({
        email,
        password,
      });

      // Redirect to tasks page on success
      router.push("/tasks");
    } catch (err: any) {
      setError(err.message || "Invalid email or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-8 space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}
```

### 9. Create useAuth Hook

**lib/hooks/useAuth.ts**:

```typescript
"use client";

import { useSession } from "@/lib/auth/client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function useAuth(requireAuth: boolean = true) {
  const router = useRouter();
  const { data: session, isLoading } = useSession();

  useEffect(() => {
    if (!isLoading && requireAuth && !session) {
      router.push("/signin");
    }
  }, [session, isLoading, requireAuth, router]);

  return {
    session,
    user: session?.user,
    isLoading,
    isAuthenticated: !!session,
  };
}
```

### 10. Protect Routes with Middleware

**middleware.ts** (root level):

```typescript
import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if accessing protected route
  const protectedRoutes = ["/tasks", "/profile"];
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );

  if (isProtectedRoute) {
    // Check for session token
    const sessionToken = request.cookies.get("todo_app.session_token")?.value;

    if (!sessionToken) {
      // Redirect to sign-in if no session
      const url = new URL("/signin", request.url);
      url.searchParams.set("redirect", pathname);
      return NextResponse.redirect(url);
    }
  }

  // Redirect authenticated users away from auth pages
  const authRoutes = ["/signin", "/signup"];
  const isAuthRoute = authRoutes.includes(pathname);

  if (isAuthRoute) {
    const sessionToken = request.cookies.get("todo_app.session_token")?.value;

    if (sessionToken) {
      // Redirect to tasks if already authenticated
      return NextResponse.redirect(new URL("/tasks", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes (except /api/auth)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!api(?!/auth)|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
```

### 11. Create Protected Page Example

**app/(dashboard)/tasks/page.tsx**:

```typescript
import { getServerSession } from "@/lib/auth/server";
import { redirect } from "next/navigation";
import { TaskList } from "@/components/tasks/TaskList";

export default async function TasksPage() {
  // Get session on server side
  const session = await getServerSession();

  // Redirect if not authenticated
  if (!session) {
    redirect("/signin");
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      <TaskList userId={session.user.id} />
    </div>
  );
}
```

### 12. Add Sign Out Functionality

**components/layout/Navbar.tsx**:

```typescript
"use client";

import { signOut } from "@/lib/auth/client";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";

export function Navbar() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push("/signin");
    } catch (error) {
      console.error("Failed to sign out:", error);
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold text-gray-900">Todo App</h1>
            <div className="hidden md:flex gap-6">
              <a href="/tasks" className="text-gray-700 hover:text-gray-900">
                Tasks
              </a>
              <a href="/profile" className="text-gray-700 hover:text-gray-900">
                Profile
              </a>
            </div>
          </div>

          {user && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700">{user.name}</span>
              <button
                onClick={handleSignOut}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
```

### 13. Get JWT Token for API Calls

**lib/api/client.ts** (updated):

```typescript
import { authClient } from "@/lib/auth/client";

async function getAuthToken(): Promise<string | null> {
  try {
    const session = await authClient.getSession();

    if (!session?.session) {
      return null;
    }

    // Get JWT token from session
    // Better Auth JWT plugin adds token to session
    return session.session.token || null;
  } catch (error) {
    console.error("Failed to get auth token:", error);
    return null;
  }
}

// Use in API client
export const apiClient = new APIClient(
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  getAuthToken
);
```

### 14. Database Migration

Better Auth automatically creates required tables on first run. The tables created are:

```sql
-- User table (created by Better Auth)
CREATE TABLE "user" (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT false,
  password TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session table (created by Better Auth)
CREATE TABLE "session" (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  expires_at TIMESTAMP NOT NULL,
  token TEXT NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account table (for OAuth providers)
CREATE TABLE "account" (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,
  provider_account_id TEXT NOT NULL,
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verification table (for email verification)
CREATE TABLE "verification" (
  id TEXT PRIMARY KEY,
  identifier TEXT NOT NULL,
  value TEXT NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Best Practices

1. **Secure Secrets**: Use strong random keys for BETTER_AUTH_SECRET and JWT_SECRET
2. **HTTPS Only**: Use HTTPS in production for secure cookie transmission
3. **Email Verification**: Enable email verification in production
4. **Password Requirements**: Enforce strong password policies
5. **Session Duration**: Configure appropriate session expiration
6. **Error Handling**: Provide clear error messages without leaking security info
7. **Rate Limiting**: Add rate limiting to auth endpoints
8. **CSRF Protection**: Better Auth includes built-in CSRF protection
9. **Token Refresh**: Implement token refresh for long-lived sessions
10. **Audit Logging**: Log authentication events for security monitoring

## Common Patterns

### Check Authentication in Server Component
```typescript
const session = await getServerSession();
if (!session) redirect("/signin");
```

### Check Authentication in Client Component
```typescript
const { user, isLoading, isAuthenticated } = useAuth();
if (!isAuthenticated) return <div>Please sign in</div>;
```

### Protected API Route
```typescript
export async function GET(request: Request) {
  const session = await getServerSession();
  if (!session) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  // Handle request
}
```

## Success Criteria

- ✅ Better Auth installed and configured
- ✅ Neon PostgreSQL connected
- ✅ Email/password authentication working
- ✅ JWT plugin configured with secret
- ✅ Sign-up page functional
- ✅ Sign-in page functional
- ✅ Sign-out functionality working
- ✅ Protected routes with middleware
- ✅ Session management configured
- ✅ JWT tokens available for API calls

## Troubleshooting

### Issue: Database connection error
**Solution**: Check DATABASE_URL format, ensure Neon database is accessible

### Issue: JWT token not available
**Solution**: Verify JWT plugin is configured, check session.session.token

### Issue: Session not persisting
**Solution**: Check cookie settings, ensure BETTER_AUTH_URL matches domain

### Issue: Password validation failing
**Solution**: Check minPasswordLength configuration, verify password requirements

## Related Skills

- `nextjs_app_router_setup`: Next.js setup
- `api_client_creation`: Using JWT in API client
- `database_connection_setup`: Database configuration

## References

- [Better Auth Documentation](https://www.better-auth.com/docs)
- [Better Auth JWT Plugin](https://www.better-auth.com/docs/plugins/jwt)
- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
