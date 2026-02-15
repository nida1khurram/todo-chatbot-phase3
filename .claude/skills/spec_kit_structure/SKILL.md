---
name: spec_kit_structure
description: Initialize GitHub Spec-Kit Plus folder structure with .spec-kit/config.yaml, specs/ directory containing overview.md, architecture.md, and subdirectories for features/, api/, database/, and ui/.
---

# Spec-Kit Plus Structure Initialization Skill

You are an expert at setting up Spec-Kit Plus project structures for spec-driven development.

## When to Use This Skill

Apply this skill when the user:
- Starts a new project and needs the Spec-Kit Plus structure
- Asks to "initialize spec-kit" or "set up specs structure"
- Wants to add spec-driven development to an existing project
- Needs the standard folder layout for specifications

## Target Structure

The complete Spec-Kit Plus structure:

```
project-root/
├── .spec-kit/
│   └── config.yaml              # Spec-Kit configuration
├── .specify/
│   ├── memory/
│   │   └── constitution.md      # Project principles
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── adr-template.md
│   │   ├── phr-template.prompt.md
│   │   └── checklist-template.md
│   └── scripts/
│       └── bash/
│           └── *.sh             # Automation scripts
├── specs/
│   ├── overview.md              # Project overview
│   ├── architecture.md          # System architecture
│   ├── features/                # Feature specifications
│   │   └── README.md
│   ├── api/                     # API specifications
│   │   └── README.md
│   ├── database/                # Database schemas
│   │   └── README.md
│   └── ui/                      # UI specifications
│       └── README.md
└── history/
    ├── adr/                     # Architecture Decision Records
    │   └── README.md
    └── prompts/                 # Prompt History Records
        ├── constitution/
        ├── general/
        └── README.md
```

## Initialization Process

### 1. Check Existing Structure

Before creating, check what already exists:

```bash
# Check for existing spec-kit structures
ls -la .spec-kit/ 2>/dev/null || echo "No .spec-kit directory"
ls -la .specify/ 2>/dev/null || echo "No .specify directory"
ls -la specs/ 2>/dev/null || echo "No specs directory"
ls -la history/ 2>/dev/null || echo "No history directory"
```

### 2. Create Directory Structure

Create all required directories:

```bash
# Core directories
mkdir -p .spec-kit
mkdir -p .specify/memory
mkdir -p .specify/templates
mkdir -p .specify/scripts/bash

# Specs directories
mkdir -p specs/features
mkdir -p specs/api
mkdir -p specs/database
mkdir -p specs/ui

# History directories
mkdir -p history/adr
mkdir -p history/prompts/constitution
mkdir -p history/prompts/general
```

### 3. Create Configuration File

Create `.spec-kit/config.yaml`:

```yaml
# Spec-Kit Plus Configuration
version: "1.0"
project:
  name: "[PROJECT_NAME]"
  description: "[PROJECT_DESCRIPTION]"

paths:
  specs: "specs"
  templates: ".specify/templates"
  memory: ".specify/memory"
  history: "history"
  adr: "history/adr"
  prompts: "history/prompts"

features:
  auto_phr: true          # Automatically create Prompt History Records
  adr_suggestions: true   # Suggest ADRs for significant decisions
  spec_validation: true   # Validate specs against templates

defaults:
  spec_template: "spec-template.md"
  plan_template: "plan-template.md"
  tasks_template: "tasks-template.md"
```

### 4. Create Overview Document

Create `specs/overview.md`:

```markdown
# [PROJECT_NAME] Overview

## Purpose

[Brief description of what this project does and why it exists]

## Goals

1. [Primary goal]
2. [Secondary goal]
3. [Tertiary goal]

## Scope

### In Scope
- [Feature/capability 1]
- [Feature/capability 2]

### Out of Scope
- [Explicitly excluded item 1]
- [Explicitly excluded item 2]

## Key Stakeholders

| Role | Responsibility |
|------|----------------|
| [Role 1] | [Responsibility] |
| [Role 2] | [Responsibility] |

## Success Criteria

- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]

## Related Documents

- [Architecture](./architecture.md)
- [Features](./features/README.md)
- [API Specifications](./api/README.md)
```

### 5. Create Architecture Document

Create `specs/architecture.md`:

```markdown
# [PROJECT_NAME] Architecture

## System Overview

[High-level description of the system architecture]

## Architecture Diagram

```
[ASCII diagram or reference to external diagram]
```

## Components

### [Component 1]
- **Purpose**: [What it does]
- **Technology**: [Stack/framework]
- **Interfaces**: [How it communicates]

### [Component 2]
- **Purpose**: [What it does]
- **Technology**: [Stack/framework]
- **Interfaces**: [How it communicates]

## Data Flow

[Description of how data moves through the system]

## Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | [Tech] | [Why] |
| Backend | [Tech] | [Why] |
| Database | [Tech] | [Why] |
| Infrastructure | [Tech] | [Why] |

## Security Architecture

- **Authentication**: [Method]
- **Authorization**: [Method]
- **Data Protection**: [Approach]

## Deployment Architecture

[Description of deployment topology]

## Related ADRs

- [ADR-001: Title](../history/adr/001-title.md)
```

### 6. Create Subdirectory READMEs

Create `specs/features/README.md`:

```markdown
# Feature Specifications

This directory contains feature specifications for [PROJECT_NAME].

## Structure

Each feature has its own directory:

```
features/
├── NNN-feature-name/
│   ├── spec.md          # Feature specification
│   ├── plan.md          # Implementation plan
│   ├── tasks.md         # Task breakdown
│   └── checklists/      # Quality checklists
└── README.md
```

## Creating a New Feature

1. Run `/sp.specify` with your feature description
2. Review and refine the generated spec
3. Run `/sp.plan` to create implementation plan
4. Run `/sp.tasks` to generate task breakdown

## Active Features

| ID | Feature | Status | Spec |
|----|---------|--------|------|
| - | - | - | - |
```

Create `specs/api/README.md`:

```markdown
# API Specifications

This directory contains API specifications for [PROJECT_NAME].

## Structure

```
api/
├── endpoints/           # Endpoint specifications
├── schemas/             # Request/response schemas
└── README.md
```

## API Documentation Format

Each API spec should include:
- Endpoint path and method
- Request parameters and body
- Response format and status codes
- Authentication requirements
- Error responses
- Example requests/responses

## API Endpoints

| Endpoint | Method | Description | Spec |
|----------|--------|-------------|------|
| - | - | - | - |
```

Create `specs/database/README.md`:

```markdown
# Database Specifications

This directory contains database schemas and specifications for [PROJECT_NAME].

## Structure

```
database/
├── schemas/             # Table/collection schemas
├── migrations/          # Migration specifications
└── README.md
```

## Schema Documentation Format

Each schema should include:
- Entity name and purpose
- Fields with types and constraints
- Relationships to other entities
- Indexes
- Example data

## Entities

| Entity | Description | Schema |
|--------|-------------|--------|
| - | - | - |
```

Create `specs/ui/README.md`:

```markdown
# UI Specifications

This directory contains UI/UX specifications for [PROJECT_NAME].

## Structure

```
ui/
├── wireframes/          # Wireframe specifications
├── components/          # Component specifications
├── flows/               # User flow specifications
└── README.md
```

## UI Documentation Format

Each UI spec should include:
- Component/screen name
- Purpose and user goal
- Layout description
- Interactions and states
- Accessibility requirements
- Related components

## Screens/Components

| Name | Type | Description | Spec |
|------|------|-------------|------|
| - | - | - | - |
```

### 7. Create History READMEs

Create `history/adr/README.md`:

```markdown
# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for [PROJECT_NAME].

## What is an ADR?

An ADR documents a significant architectural decision, including:
- Context and problem statement
- Decision drivers
- Considered options
- Decision outcome
- Consequences

## Creating an ADR

Run `/sp.adr <decision-title>` to create a new ADR.

## ADR Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| - | - | - | - |
```

Create `history/prompts/README.md`:

```markdown
# Prompt History Records

This directory contains Prompt History Records (PHRs) for [PROJECT_NAME].

## What is a PHR?

A PHR captures AI-assisted development interactions:
- Original user prompt
- AI response summary
- Files modified
- Stage (spec, plan, tasks, etc.)

## Directory Structure

```
prompts/
├── constitution/        # Constitution-related prompts
├── general/             # General prompts
├── <feature-name>/      # Feature-specific prompts
└── README.md
```

## PHRs are created automatically after each significant interaction.
```

## Validation Checklist

After initialization, verify:

```markdown
## Spec-Kit Structure Checklist

### Core Directories
- [ ] .spec-kit/ exists with config.yaml
- [ ] .specify/memory/ exists
- [ ] .specify/templates/ exists
- [ ] specs/ exists with overview.md and architecture.md

### Spec Subdirectories
- [ ] specs/features/ exists with README.md
- [ ] specs/api/ exists with README.md
- [ ] specs/database/ exists with README.md
- [ ] specs/ui/ exists with README.md

### History Directories
- [ ] history/adr/ exists with README.md
- [ ] history/prompts/ exists with README.md
- [ ] history/prompts/constitution/ exists
- [ ] history/prompts/general/ exists

### Configuration
- [ ] .spec-kit/config.yaml has valid YAML
- [ ] Project name is set in config
- [ ] Paths are correctly configured
```

## Post-Initialization Steps

After structure is created:
1. Update `specs/overview.md` with project details
2. Update `specs/architecture.md` with system design
3. Create constitution at `.specify/memory/constitution.md`
4. Begin creating feature specs with `/sp.specify`
