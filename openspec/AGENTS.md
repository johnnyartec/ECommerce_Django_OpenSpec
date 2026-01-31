# OpenSpec Agent Workflow Guide

This document explains how to work with AI agents using OpenSpec in this project.

## What is OpenSpec?

OpenSpec is a **spec-driven development workflow** that helps you build software with clear thinking, planning, and documentation. It structures your work into **changes** (feature additions, fixes, improvements) that go through a defined artifact lifecycle.

## The Workflow

### The Artifact Lifecycle

Every change goes through these phases:

```
Idea/Request
    ↓
1. Proposal (WHY and WHAT)
    ↓
2. Specs (WHAT in detail - testable requirements)
    ↓
3. Design (HOW - technical decisions)
    ↓
4. Tasks (Implementation checklist)
    ↓
5. Implementation (Execute tasks)
    ↓
6. Verification (Validate against specs)
    ↓
7. Archive (Preserve decision history)
```

### Artifact Details

#### 1. **Proposal** (`proposal.md`)

- **Purpose**: Captures WHY we're making this change and WHAT it involves at high level
- **Content**:
  - Why (problem/opportunity)
  - What changes (brief bullets)
  - Capabilities (new/modified features)
  - Impact (affected files/systems)
- **Think of it as**: The "elevator pitch" for the work

#### 2. **Specs** (`specs/<capability>/spec.md`)

- **Purpose**: Defines WHAT we're building in precise, testable terms
- **Content**:
  - User scenarios and stories with priorities
  - Functional requirements (FR-001, FR-002, etc.)
  - Acceptance scenarios (WHEN/THEN/AND format)
  - Edge cases
  - Key entities (data models)
  - Success criteria (measurable outcomes)
- **Think of it as**: The contract that implementation must fulfill

#### 3. **Design** (`design.md`)

- **Purpose**: Captures HOW we'll build it - technical decisions and tradeoffs
- **Content**:
  - Context (current state)
  - Goals / Non-Goals
  - Technical decisions with rationale
  - Architecture/approach
- **Think of it as**: The technical blueprint

#### 4. **Tasks** (`tasks.md`)

- **Purpose**: Break work into implementable checkboxes
- **Content**:
  - Numbered task list organized by category/file
  - Clear, actionable items
  - Verification steps
- **Think of it as**: Your implementation checklist

## Available Commands

### Starting New Work

#### `/opsx:new <feature-name>` - Step-by-step workflow

Use when you want to create artifacts one at a time with guidance:

```
/opsx:new add-comments-feature
```

- Creates the change directory
- Shows instructions for the first artifact
- You work through proposal → specs → design → tasks step by step
- AI waits for your input between artifacts

#### `/opsx:ff <feature-name>` - Fast-forward mode

Use when you want all artifacts created at once:

```
/opsx:ff add-comments-feature
```

- Creates the change directory
- Generates ALL artifacts in one go (proposal, specs, design, tasks)
- Gets you to implementation faster
- Best for smaller, well-understood changes

**Example workflow:**

```
User: "I want to add comments to blog posts. Please create an OpenSpec change proposal for this feature"
AI: [Uses /opsx:ff add-comments]
- Creates proposal.md
- Creates specs/comments/spec.md
- Creates design.md
- Creates tasks.md
"Ready for implementation! 🚀"
```

### Continuing Work

#### `/opsx:continue <feature-name>` - Continue artifact creation

Use when you've started a change but haven't finished all artifacts:

```
/opsx:continue add-comments-feature
```

- Checks which artifacts are done
- Creates the next artifact that's ready (dependencies satisfied)
- Repeats until all artifacts are complete

#### `/opsx:apply <feature-name>` - Implement tasks

Use when artifacts are complete and you're ready to code:

```
/opsx:apply add-comments-feature
```

- Shows the task list
- Implements each task
- Checks off tasks as they're completed
- References specs/design during implementation

### Other Commands

#### `/opsx:explore` - Thinking mode

Use when you need to investigate, research, or think through something:

```
/opsx:explore
```

- No code changes yet
- Ask questions, investigate files, draw diagrams
- Think through problems before committing to an approach
- Exit when ready to start actual work

#### `/opsx:verify <feature-name>` - Validation

Use when implementation is done and you want to verify it matches the specs:

```
/opsx:verify add-comments-feature
```

- Checks if all tasks are completed
- Validates implementation against requirements
- Checks for design coherence
- Reports any gaps or issues

#### `/opsx:archive <feature-name>` - Complete the change

Use when everything is done and tested:

```
/opsx:archive add-comments-feature
```

- Moves change to `openspec/changes/archive/YYYY-MM-DD-<name>/`
- Preserves decision history
- Cleans up active changes directory

#### `/opsx:onboard` - Tutorial

Use if you're new to OpenSpec:

```
/opsx:onboard
```

- Guided walkthrough of the full workflow
- Uses real tasks in your codebase
- Teaches by doing

## Working with AI on This Project

### Typical Interaction Flow

**For a new feature:**

1. **You**: "I want to add [FEATURE]. Please create an OpenSpec change for this"
2. **AI**: Uses `/opsx:ff feature-name` to create all artifacts
3. **AI**: Shows you the proposal, specs, design, and tasks
4. **You**: Review and provide feedback if needed
5. **You**: "Please implement this" or "Apply the tasks"
6. **AI**: Uses `/opsx:apply feature-name` to implement
7. **AI**: Checks off tasks as they're completed
8. **You**: Test the implementation
9. **You**: "Please verify the implementation"
10. **AI**: Uses `/opsx:verify feature-name` to validate
11. **You**: "Archive this change"
12. **AI**: Uses `/opsx:archive feature-name`

**For exploratory work:**

1. **You**: "I'm thinking about [IDEA] - can we explore this?"
2. **AI**: Enters explore mode
3. **AI**: Investigates, asks questions, discusses tradeoffs
4. **You**: "Let's do it - create a change for this"
5. **AI**: Exits explore and creates change with `/opsx:new` or `/opsx:ff`

### Best Practices

#### 1. **Start with Clear Intent**

Good: "I want to add comments to blog posts with nested replies and voting"
Less clear: "Can you add some features?"

#### 2. **Use Fast-Forward for Small Changes**

- Bug fixes: `/opsx:ff fix-markdown-rendering`
- Minor features: `/opsx:ff add-post-tags`
- Refactoring: `/opsx:ff extract-email-service`

#### 3. **Use Step-by-Step for Complex Changes**

- Major features: `/opsx:new user-notification-system`
- Architectural changes: `/opsx:new migrate-to-api`
- When you want to review each artifact before proceeding

#### 4. **Use Explore Mode Liberally**

- Investigating a bug before fixing
- Understanding existing code before modifying
- Researching approaches before committing
- Discussing tradeoffs

#### 5. **Keep Changes Focused**

One change = one coherent piece of work

- Good: "add-comments-feature"
- Too broad: "improve-blog-and-add-features"
- Better split: "add-comments" + "add-tags" + "add-reactions"

#### 6. **Review Specs Before Implementation**

The specs are your contract. Make sure they capture what you want before saying "implement this."

#### 7. **Archive When Done**

Don't leave changes hanging in active directory. Archive creates valuable decision history.

## File Locations

```
openspec/
├── config.yaml              # OpenSpec configuration
├── project.md              # Project context (this is given to AI)
├── changes/                # Active work
│   └── <feature-name>/     # Individual change
│       ├── proposal.md
│       ├── design.md
│       ├── specs/
│       │   └── <capability>/
│       │       └── spec.md
│       └── tasks.md
└── changes/archive/        # Completed work
    └── YYYY-MM-DD-<name>/  # Archived with timestamp
```

## Project Context

When AI creates artifacts, it has access to:

- **Tech stack**: Django 6.x, Python 3.12+, PostgreSQL, Markdown support
- **Conventions**: Model field naming (camelCase), coding style, security practices
- **Patterns**: How to add models, views, handle user content
- **Domain knowledge**: Todo system, Blog system features

All details are in [openspec/project.md](openspec/project.md).

## Tips for Effective Collaboration

### Do:

✅ Provide clear descriptions of what you want
✅ Review artifacts before implementation
✅ Ask questions during explore mode
✅ Give feedback if specs don't match your intent
✅ Test implementations before archiving
✅ Use the workflow - it creates valuable documentation

### Don't:

❌ Skip straight to "just code this" without artifacts (you lose documentation)
❌ Make changes vague ("add some improvements")
❌ Let AI make big assumptions - clarify unclear requirements
❌ Leave changes unarchived - complete the cycle

## Example Conversations

### Example 1: New Feature

```
You: I want to add a tagging system to blog posts. Users should be able
     to add multiple tags when creating/editing posts, and we need a
     tag browsing page. Please create an OpenSpec change for this.

AI: I'll create a comprehensive change for the tagging feature.
    [Creates /opsx:ff add-blog-tags]

    Created change at openspec/changes/add-blog-tags/

    ✓ Proposal: Adding tag support to blog posts with browsing
    ✓ Specs: Tag CRUD, post association, browsing interface
    ✓ Design: Many-to-many relationship, tag model, URL structure
    ✓ Tasks: 12 implementation tasks

    Ready for implementation! Review the specs at
    openspec/changes/add-blog-tags/specs/tags/spec.md

You: Looks good. Please implement it.

AI: I'll implement the tasks now.
    [Uses /opsx:apply add-blog-tags]

    ✓ Task 1.1: Create Tag model
    ✓ Task 1.2: Add many-to-many to BlogPost
    [... continues through all tasks ...]

    All tasks complete! Please test the feature.

You: Works great! Please archive this.

AI: [Uses /opsx:archive add-blog-tags]
    Archived to openspec/changes/archive/2026-01-28-add-blog-tags/
```

### Example 2: Bug Investigation

```
You: Users are reporting that code blocks in blog posts aren't rendering
     correctly. Can we investigate?

AI: [Enters explore mode]
    Let me check the markdown rendering implementation...

    [Reads utils/markdown_renderer.py, models.py, templates]

    I found the issue: The bleach sanitizer is stripping the <pre> and
    <code> tags. The allowed_tags list needs to include these.

    [Shows relevant code sections with ASCII diagram]

    Should we create a change to fix this?

You: Yes, please fix it.

AI: [Creates /opsx:ff fix-code-block-rendering]
    ✓ All artifacts created
    [Implements fix]
    ✓ Updated allowed_tags in markdown_renderer.py
    ✓ Added test case

    Fix complete!
```

### Example 3: Exploring Architecture

```
You: I'm thinking about adding an API for the blog. Let's explore
     what that would involve.

AI: [Enters explore mode]
    Let me think through the API design options...

    Current architecture: Django templates (server-side rendering)

    For an API, we have several approaches:
    1. Django REST Framework - full-featured, overkill for simple needs
    2. Django Ninja - modern, type-safe, lighter weight
    3. Plain Django JSON views - minimal, good for small APIs

    [Discusses tradeoffs, existing code structure, considerations]

    What's your primary use case for the API?

You: Mobile app access to blog posts.

AI: Then I'd recommend Django Ninja - good DX, automatic docs,
    type safety. Want me to create a change for this?

You: Yes, but just for read-only blog access first.

AI: [Creates /opsx:new add-blog-api]
    [Proceeds with artifact creation...]
```

## Additional Resources

- **OpenSpec CLI docs**: Run `openspec --help`
- **Schema documentation**: Run `openspec schemas` to see available workflows
- **This project's conventions**: See [openspec/project.md](openspec/project.md)

---

**Remember**: OpenSpec is about **structured thinking** → **clear documentation** → **confident implementation**. Use it to create better code with better documentation! 🚀
