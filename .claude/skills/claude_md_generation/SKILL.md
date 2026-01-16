---
name: claude_md_generation
description: Generate CLAUDE.md files at root level with project overview and spec navigation, and service-level files with technology stack, code patterns, file structure, common tasks, and coding standards.
---

# CLAUDE.md Generation Skill

You are an expert at creating CLAUDE.md files that provide AI assistants with essential project context for effective code assistance.

## When to Use This Skill

Apply this skill when the user:
- Sets up a new project and needs AI context files
- Asks to "create CLAUDE.md" or "generate AI context"
- Wants to improve AI assistant effectiveness in their codebase
- Has a monorepo needing service-level context files
- Needs to document project structure for AI tools

## CLAUDE.md Purpose

CLAUDE.md files provide AI assistants with:
- Project overview and navigation
- Technology stack and conventions
- Code patterns and standards
- Common tasks and commands
- File structure understanding

## File Hierarchy

```
project-root/
├── CLAUDE.md                    # Root-level: Project overview
├── services/
│   ├── api/
│   │   └── CLAUDE.md            # Service-level: API specifics
│   ├── web/
│   │   └── CLAUDE.md            # Service-level: Web frontend
│   └── worker/
│       └── CLAUDE.md            # Service-level: Background jobs
└── packages/
    └── shared/
        └── CLAUDE.md            # Package-level: Shared utilities
```

## Root-Level CLAUDE.md

The root CLAUDE.md provides project-wide context and navigation.

### Template

```markdown
# [PROJECT_NAME]

[One-sentence project description]

## Quick Start

```bash
# Install dependencies
[install command]

# Run development server
[dev command]

# Run tests
[test command]
```

## Project Overview

[2-3 paragraph description of what this project does, its main features, and target users]

## Architecture

[High-level architecture description]

```
[ASCII diagram of main components]
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | [Tech] | [Purpose] |
| Backend | [Tech] | [Purpose] |
| Database | [Tech] | [Purpose] |
| Infrastructure | [Tech] | [Purpose] |

## Project Structure

```
[project-name]/
├── src/                    # Source code
│   ├── components/         # UI components
│   ├── services/           # Business logic
│   └── utils/              # Utilities
├── tests/                  # Test files
├── specs/                  # Feature specifications
│   ├── overview.md         # Project overview
│   ├── architecture.md     # System architecture
│   └── features/           # Feature specs
├── .specify/               # Spec-Kit configuration
└── history/                # ADRs and PHRs
```

## Spec Navigation

| Document | Purpose | Location |
|----------|---------|----------|
| Constitution | Core principles | `.specify/memory/constitution.md` |
| Overview | Project scope | `specs/overview.md` |
| Architecture | System design | `specs/architecture.md` |
| Features | Feature specs | `specs/features/` |
| ADRs | Design decisions | `history/adr/` |

## Development Workflow

1. **Spec First**: Create specification before code (`/sp.specify`)
2. **Plan**: Generate implementation plan (`/sp.plan`)
3. **Tasks**: Break into testable tasks (`/sp.tasks`)
4. **Implement**: Execute tasks with tests (`/sp.implement`)
5. **Document**: Record decisions in ADRs

## Common Commands

```bash
# Development
[dev commands]

# Testing
[test commands]

# Building
[build commands]

# Deployment
[deploy commands]
```

## Code Standards

See `.specify/memory/constitution.md` for:
- Code quality standards
- Testing requirements
- Security guidelines
- Architecture principles

## Service Documentation

| Service | Description | CLAUDE.md |
|---------|-------------|-----------|
| [service1] | [description] | `services/[service1]/CLAUDE.md` |
| [service2] | [description] | `services/[service2]/CLAUDE.md` |
```

## Service-Level CLAUDE.md

Service-level files provide detailed context for specific services/packages.

### Template

```markdown
# [SERVICE_NAME] Service

[One-sentence service description]

## Purpose

[What this service does and why it exists]

## Technology Stack

- **Runtime**: [e.g., Node.js 20, Python 3.12]
- **Framework**: [e.g., Express, FastAPI, Next.js]
- **Database**: [e.g., PostgreSQL, MongoDB]
- **ORM/ODM**: [e.g., Prisma, SQLAlchemy]
- **Testing**: [e.g., Jest, pytest]

## File Structure

```
[service-name]/
├── src/
│   ├── controllers/        # Request handlers
│   ├── services/           # Business logic
│   ├── models/             # Data models
│   ├── middleware/         # Request middleware
│   ├── utils/              # Helper functions
│   └── index.ts            # Entry point
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── package.json
└── CLAUDE.md
```

## Code Patterns

### Controller Pattern

```[language]
// Controllers handle HTTP requests and delegate to services
[example code]
```

### Service Pattern

```[language]
// Services contain business logic
[example code]
```

### Repository Pattern (if applicable)

```[language]
// Repositories handle data access
[example code]
```

## API Endpoints (if applicable)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/[resource] | List resources | Required |
| POST | /api/[resource] | Create resource | Required |
| GET | /api/[resource]/:id | Get resource | Required |
| PUT | /api/[resource]/:id | Update resource | Required |
| DELETE | /api/[resource]/:id | Delete resource | Required |

## Common Tasks

### Adding a New Endpoint

1. Create controller in `src/controllers/`
2. Create service in `src/services/`
3. Add route in `src/routes/`
4. Write tests in `tests/`

### Adding a New Model

1. Define model in `src/models/`
2. Create migration (if needed)
3. Update relevant services
4. Write unit tests

### Running Tests

```bash
# All tests
[test command]

# Unit tests only
[unit test command]

# With coverage
[coverage command]
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| DATABASE_URL | Database connection | Yes | - |
| API_KEY | External API key | Yes | - |
| PORT | Server port | No | 3000 |

## Dependencies

### Key Dependencies

- `[package]`: [purpose]
- `[package]`: [purpose]
- `[package]`: [purpose]

### Dev Dependencies

- `[package]`: [purpose]
- `[package]`: [purpose]

## Coding Standards

### Naming Conventions

- **Files**: `kebab-case.ts`
- **Classes**: `PascalCase`
- **Functions**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Variables**: `camelCase`

### Import Order

1. Node built-ins
2. External packages
3. Internal modules (absolute paths)
4. Relative imports
5. Type imports

### Error Handling

```[language]
// Standard error handling pattern
[example code]
```

## Testing Standards

- Unit tests for all services
- Integration tests for API endpoints
- Minimum 80% coverage
- Test file naming: `*.test.ts` or `*.spec.ts`

## Related Documentation

- [Link to API docs]
- [Link to architecture docs]
- [Link to deployment docs]
```

## Generation Process

### 1. Analyze the Project

Before generating, gather information:

```bash
# Check project structure
ls -la
find . -name "package.json" -o -name "requirements.txt" -o -name "go.mod" | head -20

# Check existing docs
cat README.md 2>/dev/null || echo "No README"
cat .specify/memory/constitution.md 2>/dev/null || echo "No constitution"

# Check for existing CLAUDE.md
find . -name "CLAUDE.md" -type f

# Identify services/packages
ls -la services/ 2>/dev/null || echo "No services directory"
ls -la packages/ 2>/dev/null || echo "No packages directory"
```

### 2. Extract Technology Stack

Identify technologies from:
- `package.json` (Node.js projects)
- `requirements.txt` / `pyproject.toml` (Python)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- Dockerfile / docker-compose.yml
- Configuration files

### 3. Identify Code Patterns

Look for patterns in existing code:
- Directory structure conventions
- Class/function naming
- Import organization
- Error handling patterns
- Testing patterns

### 4. Generate Appropriate Level

- **Root level**: Always create for project overview
- **Service level**: Create for each service in monorepo
- **Package level**: Create for shared packages

### 5. Keep It Accurate

- Only document what actually exists
- Don't invent commands or patterns
- Reference actual file paths
- Link to real documentation

## Validation Checklist

```markdown
## CLAUDE.md Quality Checklist

### Root-Level CLAUDE.md
- [ ] Project name and description accurate
- [ ] Quick start commands are correct and tested
- [ ] Technology stack matches actual dependencies
- [ ] Project structure reflects reality
- [ ] Spec navigation links are valid
- [ ] Common commands work

### Service-Level CLAUDE.md
- [ ] Service purpose clearly stated
- [ ] Technology stack is accurate
- [ ] File structure matches actual layout
- [ ] Code patterns reflect actual codebase
- [ ] API endpoints are documented (if applicable)
- [ ] Common tasks are accurate
- [ ] Environment variables are complete
- [ ] Coding standards match team conventions
```

## Updating CLAUDE.md

CLAUDE.md files should be updated when:
- New technologies are added
- Directory structure changes significantly
- New code patterns are established
- New services/packages are added
- Commands or workflows change

Use the manual additions section to preserve custom content:

```markdown
<!-- MANUAL ADDITIONS START -->
[Custom content that should not be overwritten]
<!-- MANUAL ADDITIONS END -->
```

## Best Practices

1. **Be Accurate**: Only document what exists
2. **Be Concise**: AI context should be scannable
3. **Be Specific**: Include actual file paths and commands
4. **Stay Updated**: Refresh when project changes
5. **Layer Information**: Root for overview, service for details
6. **Link to Sources**: Reference specs, ADRs, and docs
