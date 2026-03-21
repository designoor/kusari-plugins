---
description: Translate a PRD into a step-by-step implementation plan with interfaces, function signatures, test plans, and acceptance criteria
argument-hint: <path-or-filename>
disable-model-invocation: false
---

You are orchestrating the translation of a PRD into an implementation plan.

## Input

The user provided: `$ARGUMENTS`

This is either a file path or a filename. If it is a full path, read the file directly. If it is just a filename, search the current working directory and its subdirectories to locate it. If multiple matches are found, ask the user which one they mean. If no matches are found, tell the user and stop.

## Phase 1: PRD Analysis

Once you have located and read the PRD, launch the `prd-analyzer` agent. Pass it the full contents of the PRD document.

The analyzer will:
- Identify gaps, ambiguities, and inconsistencies in the PRD
- Present them as a numbered batch of questions to the user
- After the user responds, ask follow-up questions if new ambiguities arise
- Repeat until all gaps are resolved
- Produce a structured analysis and a proposed step breakdown

## Phase 2: Implementation Planning

Count the number of steps in the proposed step breakdown.

### If 8 or fewer steps: Single-pass mode

Launch the `implementation-writer` agent. Pass it:
- The original PRD
- The structured analysis with all resolved gaps
- The proposed step breakdown

The writer produces the full implementation plan as a single markdown document.

Save as `<prd-name>-implementation.md` next to the PRD.
Report the saved path to the user.

### If more than 8 steps: Multi-pass mode

**Pass 1: Skeleton**

Launch the `implementation-writer` agent. Pass it:
- The original PRD
- The structured analysis with all resolved gaps
- The proposed step breakdown
- Instruction: produce only the skeleton. Classify each step as scaffolding or code. For each step, include the goal and dependencies. For code steps, also include interfaces (names with field names and types) and function/method signatures. For scaffolding steps, also include a file list (paths only, no content). No edge cases, test plans, acceptance criteria, or data flow.

The skeleton must follow this format:

```
# Implementation Plan: [Feature Name]

## Summary
One paragraph describing what this plan covers.

## Steps Overview

### Step 1: [Step Name] [scaffolding]
**Goal:** One sentence stating what this step accomplishes.

**Dependencies:** None

**Files:**
- `package.json`
- `tsconfig.json`
- `packages/core/package.json`
- `packages/core/tsconfig.json`
- `packages/core/src/index.ts`

### Step 2: [Step Name] [code]
**Goal:** One sentence stating what this step accomplishes.

**Dependencies:**
- **Step 1: [Step Name]** -- project structure and build pipeline

**Interfaces:**
- `UserProfile` — id: string, email: string, displayName: string, createdAt: DateTime
- `UserSettings` — userId: string, theme: enum(light, dark), notificationsEnabled: boolean

**Functions/Methods:**
- `createUserProfile(email: string, displayName: string): UserProfile` — Creates a new user profile and persists it
- `getUserProfile(id: string): UserProfile | null` — Retrieves a user profile by ID
- `updateUserSettings(userId: string, settings: Partial<UserSettings>): UserSettings` — Merges provided settings with existing ones

### Step 3: [Step Name] [code]
**Goal:** One sentence stating what this step accomplishes.

**Dependencies:**
- **Step 1: [Step Name]** -- project structure and build pipeline
- **Step 2: [Step Name]** -- `UserProfile`, `UserSettings` from `src/models/user`; `createUserProfile` from `src/services/user`
```

Create the output directory `<prd-name>-implementation/` next to the PRD.
Save the skeleton as `index.md` in that directory.

**Pass 2: Step detail**

For each batch of 3-4 steps, launch the `implementation-writer` agent. Pass it:
- The original PRD
- The structured analysis with all resolved gaps
- The full skeleton from `index.md`
- Instruction: produce full detail for steps N through M only. Use the classification tag from the skeleton ([scaffolding] or [code]) to select the correct step structure. Code steps use the full code step structure (Goal, Interfaces, Functions/Methods, Data Flow if applicable, Edge Cases & Constraints, Test Plan, Acceptance Criteria). Scaffolding steps use the scaffolding step structure (Goal, Files to Write with literal content, Post-Setup Verification).

Save each step as `step-NN-<step-name>.md` in the output directory.

After all steps are written, report the output directory path to the user.
