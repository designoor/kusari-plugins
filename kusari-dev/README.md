# kusari-dev

PRD-to-code pipeline. Plan implementation from a PRD, then execute steps with test-first development and automatic validation.

## Commands

### /plan

```
/plan <path-or-filename>
```

Translates a PRD into a step-by-step implementation plan. Argument is a PRD file path or filename.

Two-phase process:

1. **prd-analyzer** (cyan) -- Reads the PRD, identifies gaps and ambiguities, asks you to resolve them. Produces a structured analysis and proposed step breakdown.
2. **implementation-writer** (green) -- Translates the analysis into detailed implementation steps with interfaces, function signatures, test plans, and acceptance criteria.

Output for plans with 8 or fewer steps: a single `<prd-name>-implementation.md` file. For more than 8 steps: a directory with `index.md` skeleton and individual `step-NN-<name>.md` files.

### /execute

```
/execute <path-or-filename>
```

Executes a single implementation plan step. Argument is a step file path or filename (e.g., `step-03-sqlite-database.md`). Run from the target project's root directory.

For code steps:
1. **test-writer** (cyan) -- Writes test files from the step's Test Plan, locking down the contract.
2. **implementer** (green) -- Writes production code against the existing tests.
3. Orchestrator runs the project's test command (auto-detected).
4. On failure: implementer fixes production code (max 3 retries, test files never modified).
For scaffolding steps:
1. **implementer** (green) -- Writes the literal files specified in the step.
2. Orchestrator runs Post-Setup Verification commands.
3. On failure: implementer fixes (max 3 retries).

### /review

```
/review [step-file]
```

Reviews uncommitted changes before commit. Runs `git diff` and `git diff --cached` to collect changes, then launches parallel review agents to check for bugs, CLAUDE.md compliance, historical context, prior PR comments, and code comment adherence. Each finding is scored 0-100; only issues scoring 80+ are reported.

Optional argument: a step file path or filename. When provided, an additional agent checks the diff against the step specification for missing functionality, contradictions, and out-of-scope changes.

### /build

```
/build <plan-folder-or-step-file>
```

Executes implementation steps in an isolated git worktree with automatic code review after each step. Accepts either a plan folder (executes all steps sequentially) or a single step file.

For each step:
1. Executes the step (same logic as `/execute`).
2. Reviews the changes (same logic as `/review` with step-spec compliance).
3. Commits on success, stops the entire build on failure.

After all steps complete, reports the worktree path/branch and a consolidated summary of all choices and assumptions made by agents, so the user can course-correct.

## Components

| Type | Name | Used by | Purpose |
|------|------|---------|---------|
| Command | plan | /plan | Orchestrates PRD-to-plan pipeline |
| Command | execute | /execute | Orchestrates test-first step execution |
| Command | review | /review | Orchestrates multi-agent diff review |
| Command | build | /build | Executes plan in worktree with per-step review |
| Agent | prd-analyzer | /plan | Interrogates PRD for completeness |
| Agent | implementation-writer | /plan | Produces detailed step files |
| Agent | test-writer | /execute, /build | Writes tests before code |
| Agent | implementer | /execute, /build | Writes production code or scaffolding |
