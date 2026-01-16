# Next.js App Router Setup Skill

## Description
Set up Next.js 15+ project with App Router, configure TypeScript strict mode, install and configure Tailwind CSS, create app/ directory structure with layouts and pages, and set up component directories.

## When to Use
- Setting up a new Next.js 15+ project from scratch
- Initializing the frontend portion of a monorepo
- Configuring Next.js with TypeScript strict mode
- Setting up Tailwind CSS with proper configuration
- Creating the recommended App Router directory structure

## Prerequisites
- Node.js 18+ installed
- npm or pnpm package manager
- Working directory prepared for Next.js project

## Skill Steps

### 1. Initialize Next.js Project with App Router

```bash
# If in monorepo, navigate to frontend directory first
cd frontend

# Initialize Next.js with App Router and TypeScript
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Options Explained**:
- `--typescript`: Enable TypeScript
- `--tailwind`: Install and configure Tailwind CSS
- `--app`: Use App Router (app/ directory)
- `--no-src-dir`: Place app/ at root level (not in src/)
- `--import-alias "@/*"`: Set up path aliases

### 2. Configure TypeScript Strict Mode

Edit `tsconfig.json` to enable strict type checking:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    },
    "strictNullChecks": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**Key Strict Settings**:
- `strict: true`: Enable all strict type checking options
- `strictNullChecks: true`: Prevent null/undefined errors
- `noImplicitAny: true`: Require explicit types
- `noUnusedLocals: true`: Flag unused variables
- `noUnusedParameters: true`: Flag unused function parameters

### 3. Configure Tailwind CSS

Verify `tailwind.config.ts` has proper content paths:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
};
export default config;
```

### 4. Create App Router Directory Structure

```bash
# Create core app/ structure
mkdir -p app/(auth)/signin app/(auth)/signup
mkdir -p app/(dashboard)/tasks app/(dashboard)/profile
mkdir -p app/api/auth

# Create component directories
mkdir -p components/ui components/forms components/tasks components/layout

# Create lib directories for utilities
mkdir -p lib/api lib/auth lib/hooks lib/utils

# Create types directory
mkdir -p types
```

**Directory Structure**:
```
app/
├── (auth)/              # Route group for authentication pages
│   ├── signin/
│   │   └── page.tsx
│   ├── signup/
│   │   └── page.tsx
│   └── layout.tsx       # Auth layout (no navbar)
├── (dashboard)/         # Route group for authenticated pages
│   ├── tasks/
│   │   └── page.tsx
│   ├── profile/
│   │   └── page.tsx
│   └── layout.tsx       # Dashboard layout (with navbar)
├── api/                 # API routes (if needed)
│   └── auth/
│       └── [...all]/route.ts
├── layout.tsx           # Root layout
├── page.tsx             # Home page
└── globals.css          # Global styles

components/
├── ui/                  # Reusable UI components
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Card.tsx
├── forms/               # Form components
│   ├── SignInForm.tsx
│   └── SignUpForm.tsx
├── tasks/               # Task-specific components
│   ├── TaskList.tsx
│   ├── TaskCard.tsx
│   └── TaskForm.tsx
└── layout/              # Layout components
    ├── Navbar.tsx
    └── Sidebar.tsx

lib/
├── api/                 # API client utilities
│   └── client.ts
├── auth/                # Authentication utilities
│   └── auth.ts
├── hooks/               # Custom React hooks
│   └── useAuth.ts
└── utils/               # General utilities
    └── cn.ts

types/
└── index.ts             # TypeScript type definitions
```

### 5. Create Root Layout

Create `app/layout.tsx`:

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Todo App",
  description: "Full-stack todo application with Next.js and FastAPI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

### 6. Create Route Group Layouts

**Auth Layout** (`app/(auth)/layout.tsx`):

```typescript
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full">{children}</div>
    </div>
  );
}
```

**Dashboard Layout** (`app/(dashboard)/layout.tsx`):

```typescript
import { Navbar } from "@/components/layout/Navbar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
```

### 7. Create Basic Page Components

**Home Page** (`app/page.tsx`):

```typescript
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-8">Todo App</h1>
      <div className="flex gap-4">
        <Link
          href="/signin"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Sign In
        </Link>
        <Link
          href="/signup"
          className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
        >
          Sign Up
        </Link>
      </div>
    </div>
  );
}
```

**Tasks Page** (`app/(dashboard)/tasks/page.tsx`):

```typescript
export default function TasksPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Task list will appear here</p>
      </div>
    </div>
  );
}
```

### 8. Configure Environment Variables

Create `.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration (will be added later)
BETTER_AUTH_SECRET=
BETTER_AUTH_URL=http://localhost:3000
```

Create `.env.example` for documentation:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

### 9. Update package.json Scripts

Ensure `package.json` has these scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  }
}
```

### 10. Create Utility Functions

**CN Utility** (`lib/utils/cn.ts`):

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

Install dependencies for cn utility:

```bash
npm install clsx tailwind-merge
npm install -D @types/node
```

### 11. Verify Installation

```bash
# Run type checking
npm run type-check

# Start development server
npm run dev
```

Visit `http://localhost:3000` to verify the setup.

## Success Criteria

- ✅ Next.js 15+ with App Router initialized
- ✅ TypeScript strict mode enabled and passing
- ✅ Tailwind CSS configured and working
- ✅ Route groups created: (auth) and (dashboard)
- ✅ Component directories structured
- ✅ Root and route group layouts created
- ✅ Basic pages render correctly
- ✅ Environment variables configured
- ✅ Dev server runs without errors
- ✅ Type checking passes

## Common Issues and Solutions

### Issue: "Module not found" errors
**Solution**: Ensure `tsconfig.json` paths are configured correctly and restart the dev server.

### Issue: Tailwind styles not applying
**Solution**: Verify `tailwind.config.ts` content paths include all component directories.

### Issue: TypeScript errors in strict mode
**Solution**: Add explicit type annotations and handle null/undefined cases properly.

### Issue: Route group not working
**Solution**: Ensure parentheses in directory names: `(auth)` not `auth`.

## Next Steps After Setup

1. Install and configure Better Auth for authentication
2. Create API client utilities in `lib/api/client.ts`
3. Implement authentication forms in `components/forms/`
4. Create reusable UI components in `components/ui/`
5. Set up task-related components in `components/tasks/`

## Related Skills

- `better_auth_setup`: Configure Better Auth with JWT
- `api_client_setup`: Create type-safe API client
- `ui_component_library`: Build reusable UI components

## References

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
- [Tailwind CSS with Next.js](https://tailwindcss.com/docs/guides/nextjs)
