---
name: spec_writing
description: Write feature specifications with overview, user stories in "As a [user], I can [action] so that [benefit]" format, testable acceptance criteria with edge cases, technical constraints, and success metrics following Spec-Kit Plus conventions.
---

# Spec Writing Skill

You are an expert at writing clear, testable feature specifications using Spec-Driven Development (SDD) methodology.

## When to Use This Skill

Apply this skill when the user:
- Describes a feature they want to build
- Asks to "write a spec" or "create a specification"
- Needs to document requirements for a feature
- Wants to formalize a feature idea into actionable requirements

## Spec Writing Process

### 1. Understand the Feature

Before writing, extract from the user's description:
- **Actors**: Who uses this feature?
- **Actions**: What do they do?
- **Data**: What information is involved?
- **Constraints**: What limitations or rules apply?

### 2. Generate a Feature Name

Create a concise 2-4 word branch name:
- Use action-noun format (e.g., "user-auth", "payment-processing")
- Preserve technical terms (OAuth2, API, JWT)
- Keep descriptive but brief

### 3. Check for Existing Features

Before creating a new spec:
```bash
git fetch --all --prune
git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-'
ls specs/ 2>/dev/null || echo "No specs directory"
```

Find the highest feature number and use N+1 for the new feature.

### 4. Create the Spec Structure

Use the template at `.specify/templates/spec-template.md` and create:
```
specs/<NNN-feature-name>/
├── spec.md
└── checklists/
    └── requirements.md
```

Run the setup script:
```bash
.specify/scripts/bash/create-new-feature.sh --json "<description>" --number <N> --short-name "<feature-name>"
```

### 5. Write User Scenarios & Testing (Mandatory)

Create prioritized, independently testable user stories:

```markdown
### User Story 1 - [Brief Title] (Priority: P1)

[Plain language description of user journey]

**Why this priority**: [Business value explanation]

**Independent Test**: [How to test this story in isolation]

**Acceptance Scenarios**:
1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]
```

**Priority Guidelines:**
- **P1**: Core MVP functionality - must have for launch
- **P2**: Important enhancements - needed soon after MVP
- **P3**: Nice-to-have improvements - future iterations

**Independence Test:** Each story should:
- Be developable independently
- Be testable independently
- Be deployable independently
- Deliver standalone value

### 6. Write Functional Requirements (Mandatory)

Create testable, numbered requirements:

```markdown
### Functional Requirements

- **FR-001**: System MUST [specific capability]
- **FR-002**: Users MUST be able to [key interaction]
- **FR-003**: System MUST [data/behavior requirement]
```

**Requirement Writing Rules:**
- Each requirement must be testable
- Use MUST, SHOULD, MAY consistently
- No implementation details (no frameworks, APIs, languages)
- Focus on WHAT, not HOW

### 7. Define Success Criteria (Mandatory)

Create measurable, technology-agnostic outcomes:

```markdown
### Measurable Outcomes

- **SC-001**: [User-focused metric, e.g., "Users complete task in under 2 minutes"]
- **SC-002**: [Performance metric, e.g., "System handles 1000 concurrent users"]
- **SC-003**: [Quality metric, e.g., "90% task completion on first attempt"]
```

**Success Criteria Rules:**
- Must be measurable (include numbers)
- Must be technology-agnostic
- Must be user/business focused
- Must be verifiable without implementation knowledge

**Good Examples:**
- "Users can complete checkout in under 3 minutes"
- "Search results appear in under 1 second"

**Bad Examples (avoid):**
- "API response time under 200ms" (too technical)
- "React components render efficiently" (framework-specific)

### 8. Identify Edge Cases

Document boundary conditions and error scenarios:

```markdown
### Edge Cases

- What happens when [boundary condition]?
- How does system handle [error scenario]?
- What if [unusual but valid input]?
```

### 9. Handle Unclear Requirements

**Make informed guesses** using context and industry standards for:
- Data retention (use industry standards)
- Performance targets (standard web app expectations)
- Error handling (user-friendly messages)
- Authentication (session-based or OAuth2)
- Integration patterns (RESTful APIs)

**Only use [NEEDS CLARIFICATION: specific question]** when:
- Choice significantly impacts feature scope
- Multiple reasonable interpretations exist
- No reasonable default exists

**Maximum 3 clarification markers.** Prioritize by:
1. Scope impact
2. Security/privacy concerns
3. User experience implications
4. Technical details (lowest priority)

### 10. Validate the Spec

Create a quality checklist at `specs/<feature>/checklists/requirements.md`:

```markdown
# Specification Quality Checklist: [FEATURE NAME]

## Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

## Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Success criteria are technology-agnostic
- [ ] All acceptance scenarios are defined
- [ ] Edge cases are identified
- [ ] Scope is clearly bounded

## Feature Readiness
- [ ] All functional requirements have clear acceptance criteria
- [ ] User scenarios cover primary flows
- [ ] Feature meets measurable outcomes
- [ ] No implementation details leak into specification
```

Validate the spec against each item. If items fail:
1. List failing items with specific issues
2. Update spec to address each issue
3. Re-validate (max 3 iterations)

### 11. Report Completion

After successful spec creation, report:
- Branch name created
- Spec file path
- Checklist validation results
- Readiness for next phase (`/sp.plan`)

## Key Principles

1. **WHAT not HOW**: Specs describe what users need, not how to implement
2. **Business language**: Written for stakeholders, not developers
3. **Testable requirements**: Every requirement can be verified
4. **Independent stories**: Each user story delivers standalone value
5. **Measurable success**: Criteria include specific metrics
6. **Minimal clarification**: Make informed defaults, ask only critical questions

## File Locations

- **Spec template**: `.specify/templates/spec-template.md`
- **Feature specs**: `specs/<NNN-feature-name>/spec.md`
- **Checklists**: `specs/<NNN-feature-name>/checklists/requirements.md`
- **Setup script**: `.specify/scripts/bash/create-new-feature.sh`

## Next Steps After Spec

Once the spec is complete:
1. User can run `/sp.clarify` to resolve any remaining questions
2. User can run `/sp.plan` to create a technical implementation plan
3. User can run `/sp.tasks` to break the plan into executable tasks
