---
id: 1
title: Create Todo Fullstack Auth
stage: spec
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 1-todo-fullstack-auth
branch: 1-todo-fullstack-auth
user: user
command: /sp.specify
labels: [todo, auth, fullstack, web]
links:
  spec: specs/1-todo-fullstack-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-todo-fullstack-auth/spec.md
 - specs/1-todo-fullstack-auth/checklists/requirements.md
tests:
 - none
---

## Prompt

```text
# Phase II: Todo Full-Stack Web Application - Basic Level (Multi-user Web + Auth + Persistence)

**Objective**
Transform the existing console todo application into a secure, multi-user, full-stack web application with persistent storage, RESTful API, responsive frontend, and JWT-based authentication using Better Auth.

**Current Phase**
Phase II: Web Application + Authentication

**Target Outcome**
A production-ready monorepo todo app where authenticated users can only see and manage their own tasks via browser.

**Primary Agents to Engage** (in recommended order)

1. **spec-driven-dev.md**          → Overall orchestration, spec writing/updating, task breakdown
2. **authentication-agent.md**     → Better Auth + JWT setup (critical first step)
3. **fastapi-backend-agent.md**    → REST API, SQLModel, JWT middleware, database
4. **nextjs-frontend-agent.md**    → UI, API client, protected routes, server/client components

**Core Skills to Activate** (priority order)

| Priority | Skill                          | Primary Agent(s) used with this skill              | Purpose / When to use                                   |
|----------|--------------------------------|----------------------------------------------------|----------------------------------------------------------|
| 1        | better_auth_setup              | authentication-agent                               | Configure Better Auth with JWT plugin (frontend)        |
| 2        | jwt_verification               | fastapi-backend-agent                              | FastAPI middleware to verify & extract user from JWT    |
| 3        | fastapi_project_setup          | fastapi-backend-agent                              | Project structure, dependencies, main app               |
| 4        | database_connection_setup      | fastapi-backend-agent                              | Neon PostgreSQL + SQLModel connection                   |
| 5        | pydantic_schema_creation       | fastapi-backend-agent                              | TaskCreate/TaskRead/TaskUpdate schemas                  |
| 6        | restful_api_design             | fastapi-backend-agent                              | CRUD + complete endpoints with user ownership filter    |
| 7        | nextjs_app_router_setup        | nextjs-frontend-agent                              | App Router structure, layouts, pages                    |
| 8        | protected_route_implementation | nextjs-frontend-agent                              | Server-side protected pages + middleware                |
| 9        | client_component_patterns      | nextjs-frontend-agent                              | Interactive forms, task list with optimistic updates    |
| 10       | server_component_patterns      | nextjs-frontend-agent                              | Data fetching in server components                      |
| 11       | data_validation                | fastapi-backend-agent + nextjs-frontend-agent      | Input validation (both sides)                           |

**Success Criteria** (must all be achieved)

- [ ] User can sign up / sign in using Better Auth (email/password)
- [ ] JWT token is issued and attached to every API request from frontend
- [ ] All API endpoints return 401 if no/invalid token
- [ ] Every task operation is scoped only to the authenticated user (user_id filter enforced)
- [ ] Full CRUD + toggle complete on tasks works end-to-end
- [ ] Data persists in Neon PostgreSQL (tasks table with user_id FK)
- [ ] Frontend is responsive and uses Tailwind + modern Next.js patterns
- [ ] Project follows monorepo Spec-Kit structure perfectly
- [ ] docker-compose starts both services correctly

**Non-Goals / Out of Scope for Phase II**

- Real-time updates (websockets, server-sent events)
- Task categories, tags, due dates, priorities
- Advanced filtering/sorting/pagination
- Password reset, social login, 2FA
- Rate limiting, logging, monitoring
- Dark mode, accessibility improvements
- Deployment (Vercel + Render/Fly.io etc.)
- Phase III chatbot integration

**Execution Strategy (recommended sequence)**

1. spec-driven-dev → Finalize/update these specs first:
   - sp.specify.md (this file)
   - features/authentication.md
   - features/task-crud.md
   - api/rest-endpoints.md
   - database/schema.md

2. authentication-agent + better_auth_setup + jwt_verification
   → Set up auth foundation (frontend + backend verification)

3. fastapi-backend-agent
   → Database → Models → JWT middleware → Protected CRUD routes

4. nextjs-frontend-agent
   → Auth pages → API client with JWT → Protected task pages + components

5. spec-driven-dev (iteration loop)
   → Test → Fix → Update specs if needed → Repeat

**Important Reminders for All Agents**

- Always reference specs with @specs/path/to/file.md syntax
- Use environment variables: DATABASE_URL, BETTER_AUTH_SECRET (shared!)
- Enforce user ownership on **every** database query
- Return clear HTTP status codes + JSON error messages
- Prefer server components; use client components only for interactivity
```

## Response snapshot

Created the feature specification for the Todo Full-Stack Web Application with Authentication (Phase II). The specification includes:

1. **User Stories**:
   - User registration and authentication (P1)
   - Secure todo management (P1)
   - Multi-user data isolation (P2)

2. **Functional Requirements**: 12 detailed requirements covering authentication, task management, data isolation, and security

3. **Key Entities**: User and Task entities defined

4. **Success Criteria**: 7 measurable outcomes focused on user experience and system security

5. **Edge Cases**: Security considerations for data isolation, JWT handling, and concurrent access

The specification follows the template structure and is ready for the planning phase. All requirements are testable and technology-agnostic, focusing on user value rather than implementation details.

## Outcome

- ✅ Impact: Complete feature specification for Phase II todo app with authentication
- 🧪 Tests: No tests required for specification creation
- 📁 Files: Created spec.md and requirements checklist in specs/1-todo-fullstack-auth/
- 🔁 Next prompts: Ready for /sp.plan to generate implementation plan
- 🧠 Reflection: Specification covers all critical aspects of multi-user authentication and task management

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Execute /sp.plan to generate implementation plan