---
name: constitution_creation
description: Create constitution.md files defining project vision, core principles like spec-driven and AI-first development, development constraints, technology stack decisions with justifications, quality standards, and success criteria.
---

# Constitution Creation Skill

You are an expert at creating project constitutions that establish foundational principles, constraints, and standards for software projects following Spec-Driven Development (SDD) methodology.

## When to Use This Skill

Apply this skill when the user:
- Starts a new project and needs foundational principles
- Asks to "create a constitution" or "define project principles"
- Needs to establish development standards and constraints
- Wants to document technology stack decisions with justifications
- Needs to formalize quality gates and success criteria

## Constitution Structure

A constitution defines the immutable (or rarely changed) principles that govern a project. It lives at `.specify/memory/constitution.md`.

### Required Sections

1. **Project Header**: Name and brief purpose
2. **Core Principles**: 4-7 foundational principles with descriptions
3. **Development Constraints**: Technology and process requirements
4. **Quality Standards**: Testing, code quality, and review requirements
5. **Governance**: Amendment process and compliance rules
6. **Version Info**: Version number, ratification date, last amended

## Constitution Writing Process

### 1. Gather Project Context

Before writing, understand:
- **Project purpose**: What problem does this solve?
- **Team context**: Solo developer, small team, enterprise?
- **Technology preferences**: Any existing stack decisions?
- **Development philosophy**: Agile, TDD, AI-assisted?

### 2. Define Core Principles

Create 4-7 principles that reflect the project's philosophy. Each principle should:
- Have a clear, memorable name
- Include a concise description
- Be actionable (teams can verify compliance)
- Be stable (rarely needs changing)

**Common Principle Categories:**

| Category | Example Principles |
|----------|-------------------|
| Development Process | Spec-Driven, Test-First, AI-First |
| Architecture | Library-First, Microservices, Monolith |
| Quality | Zero-Bug Policy, Code Review Required |
| Simplicity | YAGNI, Minimal Dependencies, DRY |
| Communication | CLI Interface, API-First, Event-Driven |

### 3. Write Each Principle

Use this format:

```markdown
### I. [Principle Name]

[One-sentence summary of the principle]

**Guidelines:**
- [Specific guideline 1]
- [Specific guideline 2]
- [Specific guideline 3]

**Rationale:** [Why this principle matters for this project]
```

### 4. Document Technology Stack (if applicable)

```markdown
## Technology Stack

### Core Technologies
- **Language**: [Language] - [Justification]
- **Framework**: [Framework] - [Justification]
- **Database**: [Database] - [Justification]

### Development Tools
- **Package Manager**: [Tool]
- **Testing Framework**: [Tool]
- **CI/CD**: [Tool]
```

### 5. Define Quality Standards

```markdown
## Quality Standards

### Code Quality
- [Standard 1, e.g., "All code must pass linting"]
- [Standard 2, e.g., "Functions must have clear single responsibility"]

### Testing Requirements
- [Requirement 1, e.g., "Unit test coverage minimum 80%"]
- [Requirement 2, e.g., "Integration tests for all API endpoints"]

### Review Process
- [Process 1, e.g., "All PRs require at least one approval"]
- [Process 2, e.g., "Security-sensitive changes require security review"]
```

### 6. Establish Governance

```markdown
## Governance

- Constitution supersedes all other documentation
- Amendments require: documented rationale, team approval, migration plan
- All PRs must verify compliance with core principles
- Exceptions require explicit documentation and approval

**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
```

## Example Principles by Project Type

### Web Application (AI-First)

```markdown
### I. Spec-Driven Development

Every feature begins with a specification before implementation.

**Guidelines:**
- Write spec.md before any code
- Specs define WHAT, not HOW
- All acceptance criteria must be testable

### II. AI-First Development

Leverage AI assistance throughout the development lifecycle.

**Guidelines:**
- Use AI for spec generation, code review, testing
- Maintain clear context through documentation
- Verify AI outputs against specifications

### III. Test-First (Non-Negotiable)

Tests are written before implementation code.

**Guidelines:**
- Red-Green-Refactor cycle strictly enforced
- Tests must fail before implementation
- Coverage requirements enforced at CI level
```

### CLI Tool

```markdown
### I. Library-First

Every feature starts as a standalone, testable library.

**Guidelines:**
- Libraries must be independently testable
- Clear purpose required - no organizational-only libraries
- Self-contained with documented interfaces

### II. Text I/O Protocol

All interfaces use text-based input/output.

**Guidelines:**
- stdin/args for input, stdout for output, stderr for errors
- Support both JSON and human-readable formats
- Errors must be actionable and descriptive
```

## Validation Checklist

Before finalizing a constitution, verify:

```markdown
## Constitution Quality Checklist

### Structure
- [ ] Project name and purpose clearly stated
- [ ] 4-7 core principles defined
- [ ] Each principle has name, description, and guidelines
- [ ] Technology stack documented (if applicable)
- [ ] Quality standards defined
- [ ] Governance section included
- [ ] Version and dates specified

### Content Quality
- [ ] Principles are actionable (can verify compliance)
- [ ] Principles are stable (won't change frequently)
- [ ] No implementation details in principles
- [ ] Technology choices have justifications
- [ ] Quality standards are measurable
- [ ] Governance process is clear

### Consistency
- [ ] Principles don't contradict each other
- [ ] Quality standards align with principles
- [ ] Technology stack supports principles
```

## File Location

- **Constitution file**: `.specify/memory/constitution.md`
- **Template**: `.specify/templates/constitution-template.md` (if exists)

## Next Steps After Constitution

Once the constitution is complete:
1. User can run `/sp.specify` to create feature specifications
2. User can run `/sp.plan` to create implementation plans
3. All future work should reference and comply with the constitution
