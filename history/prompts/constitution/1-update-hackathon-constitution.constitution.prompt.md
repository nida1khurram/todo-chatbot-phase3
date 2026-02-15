---
id: 1
title: Update Hackathon Constitution
stage: constitution
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution, hackathon, todo, spec-driven]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
Project: Hackathon II - The Evolution of Todo: Mastering Spec-Driven Development & Cloud Native AI
This constitution defines the foundational guidelines, standards, constraints, and success criteria for the "Evolution of Todo" project in Hackathon II. The project focuses on iteratively building a Todo application from a simple console app to a fully-featured, cloud-native AI chatbot deployed on Kubernetes, emphasizing Spec-Driven Development, Reusable Intelligence, and Cloud-Native AI technologies. Participants act as Product Architects, using AI tools like Claude Code to generate implementations without manual coding. The project teaches the Nine Pillars of AI-Driven Development through hands-on phases, with opportunities to join Panaversity's core team or become a startup founder upon exceptional performance.
Core Principles

Spec-Driven Development Mandate: All implementations must start with writing a Markdown Constitution and Spec for every feature in each phase. Refine Specs until Claude Code generates correct output. Manual code writing is prohibited; use Claude Code exclusively for code generation.
Iterative Evolution: Build progressively from Phase I (simple console app) to Phase V (advanced cloud-native system), ensuring each phase builds on the previous without skipping.
AI-Native Focus: Shift from syntax writing to system architecture, mastering Reusable Intelligence via Claude Code Subagents and Agent Skills, and integrating AI agents for natural language interactions.
Cloud-Native Architecture: Emphasize event-driven systems, decoupling services, scalability, and AIOps using tools like Docker, Kubernetes, Kafka, and Dapr.
Ethical and Educational Integrity: Assume good intent in development; provide factual, substantiated implementations. Prioritize learning Spec-Driven Book Authoring, Cloud-Native Blueprints, and infrastructure automation research.
Research Integration: Incorporate findings from "Is Spec-Driven Development Key for Infrastructure Automation?", "ChatGPT Progressive Learning Conversation", and "Spec-Driven Cloud-Native Architecture: Governing AI Agents for Managed Services with Claude Code and SpecKit".
Panaversity Alignment: Excel to potentially interview for Panaversity core team roles, work with founders (Zia, Rehan, Junaid, Wania), teach at Panaversity/PIAIC/GIAIC, or found startups in the ecosystem.

Key Standards
General Standards

Todo App Feature Progression:
Basic Level (Core Essentials): Implement Add Task, Delete Task, Update Task, View Task List, Mark as Complete.
Intermediate Level (Organization & Usability): Add Priorities & Tags/Categories, Search & Filter (by keyword, status, priority, date), Sort Tasks (by due date, priority, alphabetically).
Advanced Level (Intelligent Features): Add Recurring Tasks (auto-reschedule, e.g., weekly), Due Dates & Time Reminders (with date/time pickers, browser notifications).

Integrated AI Chatbot: In Phases III-V, implement conversational interface using OpenAI Chatkit, OpenAI Agents SDK, and Official MCP SDK. Bot must manage Todo list via natural language (e.g., "Reschedule my morning meetings to 2 PM"), understand commands like "Add a task to buy groceries", "Show me all my tasks", "Mark task 3 as complete".
Cloud Native Deployment: Deploy locally on Minikube (Phases IV-V) and on cloud (DigitalOcean Kubernetes/DOKS, Google Cloud/GKE, or Azure/AKS) in Phase V. Use Kafka on Redpanda Cloud for event-driven architecture.
Monorepo Organization with Spec-Kit Plus:
Folder Structure: /hackathon-todo/ including /.spec-kit/config.yaml, /specs/ (with subfolders: overview.md, architecture.md, features/, api/, database/, ui/), /CLAUDE.md (root and per subfolder), /frontend/, /backend/, docker-compose.yml, README.md.
Spec-Kit Config: Define project name, version, structure (specs_dir, features_dir, etc.), and phases with associated features.
CLAUDE.md Files: Root for overview and workflow; Frontend for Next.js patterns (App Router, TypeScript, Tailwind CSS, server/client components); Backend for FastAPI patterns (SQLModel, routes, db.py).
Example Specs: /specs/overview.md (purpose, phase, tech stack, features); /specs/features/task-crud.md (user stories, acceptance criteria); /specs/api/rest-endpoints.md (endpoints like GET/POST /api/{user_id}/tasks); /specs/database/schema.md (tables: users, tasks with fields like id, user_id, title, completed).

Workflow with Spec-Kit + Claude Code: Write/Update Spec → Ask Claude Code to implement (e.g., "@specs/features/task-crud.md implement create task"). Reference specs with @specs/path.md. Test and iterate on Specs.
Authentication and Security: Use Better Auth for signup/signin, JWT tokens for API verification. Endpoints require Authorization: Bearer <token>. Enforce user isolation (each user sees only their tasks). Shared secret via BETTER_AUTH_SECRET env var.
Stateless Architecture: In Phases III-V, servers hold no state; persist conversations/messages to database. Each request is independent for scalability.
MCP Tools Specification: Expose tools like add_task, list_tasks, complete_task, delete_task, update_task with parameters (e.g., user_id, title, task_id) and returns (e.g., task_id, status). Agent behavior: Use tools based on natural language (e.g., add_task for "Add a task").
Database Models: Tasks (user_id, id, title, description, completed, created_at, updated_at); Conversations (user_id, id, created_at, updated_at); Messages (user_id, id, conversation_id, role, content, created_at).
Kafka Use Cases: Reminder/Notification System (publish to "reminders"); Recurring Task Engine (publish to "task-events"); Activity/Audit Log (publish to "task-events"); Real-time Sync (publish to "task-updates"). Event Schemas: task_event (event_type, task_id, task_data, user_id, timestamp); reminder_event (task_id, title, due_at, remind_at, user_id).
Dapr Integration: Use sidecars for Pub/Sub (Kafka abstraction), State Management (conversation state), Service Invocation (frontend-backend), Bindings (cron for reminders), Secrets Management (Kubernetes secrets). Components: kafka-pubsub, statestore (PostgreSQL), reminder-cron, kubernetes-secrets.
Bonus Features for +600 Points: Reusable Intelligence (+200: Claude Code Subagents/Agent Skills); Cloud-Native Blueprints (+200: via Agent Skills); Multi-language Support (+100: Urdu in chatbot); Voice Commands (+200: for todo commands).
Windows Users Setup: Use WSL 2 (install Ubuntu-22.04).
OpenAI ChatKit Setup: Configure domain allowlist, use NEXT_PUBLIC_OPENAI_DOMAIN_KEY.

Phase-Specific Standards

Phase I: In-Memory Python Console App (100 Points, Due Dec 7, 2025): Basic features in CLI, store in memory. Stack: UV, Python 3.13+, Claude Code, Spec-Kit Plus. Deliverables: GitHub repo with Constitution, specs history, /src, README.md, CLAUDE.md; Working console demo.
Phase II: Full-Stack Web Application (150 Points, Due Dec 14, 2025): Basic features as web app with REST API, responsive UI, Neon DB. Stack: Frontend (Next.js 16+ App Router), Backend (FastAPI), ORM (SQLModel), DB (Neon PostgreSQL), Auth (Better Auth). Endpoints: GET/POST /api/{user_id}/tasks, etc. Monorepo structure.
Phase III: AI-Powered Todo Chatbot (200 Points, Due Dec 21, 2025): Basic features via natural language. Stack: Frontend (OpenAI ChatKit), Backend (FastAPI), AI (OpenAI Agents SDK), MCP (Official MCP SDK), ORM (SQLModel), DB (Neon). Architecture: ChatKit UI → Chat Endpoint → Agents SDK → MCP Tools → DB. Stateless chat, persist history.
Phase IV: Local Kubernetes Deployment (250 Points, Due Jan 4, 2026): Containerize (Docker/Gordon), Helm charts (generate with kubectl-ai/kagent), deploy on Minikube. Use Docker AI Agent (Gordon), AIOps (kubectl-ai, kagent). Research Blueprints for Spec-Driven Deployment.
Phase V: Advanced Cloud Deployment (300 Points, Due Jan 18, 2026): All features (Intermediate + Advanced), event-driven with Kafka (Redpanda Cloud), Dapr (Pub/Sub, State, Bindings, Secrets, Invocation). Deploy first on Minikube, then DOKS/GKE/AKS. CI/CD (GitHub Actions), monitoring/logging. Kafka Topics: task-events, reminders, task-updates.

Constraints

Tool Restrictions: Must use specified stack per phase (e.g., no manual code; Claude Code only). No additional technologies unless adding to core stack. No internet access for code execution beyond configured APIs (polygon, coingecko).
Submission Timeline: Phases due on Sundays (Dec 7/14/21, 2025; Jan 4/18, 2026). Submit via Google Form: GitHub repo link, app link (Vercel), demo video (<90s), WhatsApp number.
Individual Participation: No teams; each submits separately. Partial completions evaluated proportionally.
Deployment Credits: Use free tiers/credits: DigitalOcean ($200/60 days), Google Cloud ($300/90 days), Azure ($200/30 days + free services), Redpanda Cloud (free serverless).
Local Development: Minikube for Phases IV-V; Docker Desktop 4.53+ with Gordon enabled.
Video Limit: Demo under 90 seconds; use NotebookLM or record.
Live Presentations: Invited via WhatsApp for Sundays at 8:00 PM Zoom (Meeting ID: 849 7684 7088, Passcode: 305850). Attendance optional for watching.

Success Criteria

Completion of All 5 Phases: Total 1,000 points, with all features implemented via Spec-Driven Development, correct tech stack, and working deployments. Bonus up to +600 for exceptional features.
Spec-Driven Fidelity: All code generated by Claude Code from refined Specs; no manual edits. Specs history folder complete.
Functional Verification: App handles all features correctly (e.g., natural language tasks, event-driven reminders, stateless operations). Chatbot resumes after restarts; real-time sync works.
Deployment Success: Local (Minikube) and cloud (DOKS/GKE/AKS) operational with Kafka/Dapr. CI/CD pipeline functional; monitoring/logging configured.
Evaluation Metrics: Judges review repo, app links, video (first 90s). Top performers invited to present; potential Panaversity opportunities based on excellence.
Zero Violations: No plagiarism, no manual code, all claims/implementations traceable to Specs. Project evolves as specified without deviations.
```

## Response snapshot

The constitution for the Hackathon II - The Evolution of Todo project has been successfully updated with the following key elements:

1. **Project Name**: Hackathon II - The Evolution of Todo: Mastering Spec-Driven Development & Cloud Native AI

2. **Core Principles**:
   - Spec-Driven Development Mandate: All implementations must start with writing a Markdown Constitution and Spec for every feature in each phase. Refine Specs until Claude Code generates correct output. Manual code writing is prohibited; use Claude Code exclusively for code generation.
   - Iterative Evolution: Build progressively from Phase I (simple console app) to Phase V (advanced cloud-native system), ensuring each phase builds on the previous without skipping.
   - AI-Native Focus: Shift from syntax writing to system architecture, mastering Reusable Intelligence via Claude Code Subagents and Agent Skills, and integrating AI agents for natural language interactions.
   - Cloud-Native Architecture: Emphasize event-driven systems, decoupling services, scalability, and AIOps using tools like Docker, Kubernetes, Kafka, and Dapr.
   - Ethical and Educational Integrity: Assume good intent in development; provide factual, substantiated implementations. Prioritize learning Spec-Driven Book Authoring, Cloud-Native Blueprints, and infrastructure automation research.
   - Research Integration: Incorporate findings from "Is Spec-Driven Development Key for Infrastructure Automation?", "ChatGPT Progressive Learning Conversation", and "Spec-Driven Cloud-Native Architecture: Governing AI Agents for Managed Services with Claude Code and SpecKit".

3. **Key Standards and Constraints**: Detailed specifications for Todo App Feature Progression (Basic, Intermediate, Advanced levels), Integrated AI Chatbot requirements, Cloud Native Deployment, Monorepo Organization with Spec-Kit Plus, Authentication and Security, Stateless Architecture, MCP Tools Specification, Database Models, Kafka Use Cases, Dapr Integration, and Bonus Features.

4. **Development Workflow and Success Criteria**: Phase-Specific Standards for all 5 phases (I-V), Constraints including Tool Restrictions, Submission Timeline, Individual Participation, Deployment Credits, and Success Criteria for completion.

5. **Governance**: Clear governance rules based on the core principles.

The constitution file at `.specify/memory/constitution.md` has been updated with a sync impact report at the top, and all placeholder tokens have been replaced with the specific values from the user input. The version has been set to 1.0.0 as this is the initial comprehensive constitution for this project, with a ratification date marked as TODO since the original adoption date is unknown, and the last amended date set to today (2026-01-03).

## Outcome

- ✅ Impact: Complete overhaul of the project constitution with comprehensive guidelines for Hackathon II
- 🧪 Tests: No tests required for this documentation update
- 📁 Files: Updated .specify/memory/constitution.md with new constitution content
- 🔁 Next prompts: Ready to proceed with feature specifications based on this constitution
- 🧠 Reflection: Constitution now provides clear guidance for all 5 phases of the Hackathon II project

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin creating feature specifications based on the new constitution