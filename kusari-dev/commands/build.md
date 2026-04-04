---
allowed-tools: Bash(gh pr view:*), Bash(gh pr list:*), Bash(gh pr diff:*), Bash(git worktree:*), Bash(git branch:*), Bash(git checkout:*)
description: Execute an implementation plan (or single step) in an isolated git worktree, with code review after each step
argument-hint: <plan-folder-or-step-file>
disable-model-invocation: false
---

Execute implementation steps in an isolated git worktree. After each step, review the changes. If given a plan folder, execute all steps sequentially. If given a single step file, execute only that step. Stop on any failure and surface it to the user.

## Input

The user provided: `$ARGUMENTS`

This is either a path to an implementation plan folder (containing `index.md` and `step-NN-*.md` files) or a path/filename of a single step file.

- If it is a full path, check if it is a directory or file.
- If it is just a name, search the current working directory and its subdirectories. If multiple matches are found, ask the user which one they mean. If no matches are found, tell the user and stop.
- If it is a directory, it must contain an `index.md` and at least one `step-NN-*.md` file. If not, tell the user and stop.
- If it is a file, locate its sibling `index.md` in the same directory.

## Setup

1. Read `index.md` (from the plan folder, or sibling to the step file).
2. Determine the step list:
   - **Folder input:** collect all `step-NN-*.md` files, sorted by step number.
   - **Single step input:** the list contains only that one step file.
3. Create an isolated git worktree:
   - Generate a branch name: `build/<plan-folder-name>` (or `build/<step-filename>` for single steps).
   - Run `git worktree add <worktree-path> -b <branch-name>` where `<worktree-path>` is a temporary directory (e.g., `../<repo-name>-build-<timestamp>`).
   - `cd` into the worktree directory. All subsequent work happens there.

## Execution Loop

For each step in the step list, in order:

### Phase 1: Execute

1. Read `commands/execute.md` (sibling to this file).
2. Follow its Setup step 4 (step type detection) for the current step.
3. Follow its "Execution: Scaffolding Steps" or "Execution: Code Steps" section as appropriate. Skip its Input and Setup steps 1-3 -- those are already handled above.
4. If execution fails after retries, stop the entire build and report the failure to the user. Include the step name, the failing command/test, and its output.
5. Record a summary of what was done: what was implemented, what choices or assumptions the agents made, and test results (for code steps).

### Phase 2: Review

1. Read `commands/review.md` (sibling to this file).
2. Follow its steps, starting from step 1 (diff collection). Skip its Input and Setup sections -- the step file and index.md are already loaded.
3. Pass the current step file as the step-file argument so Agent #6 (spec compliance) is included.
4. The review must always produce its full report table with every issue found, regardless of score. This table is shown to the user even when the build continues. Do not stop the build based on issue scores. The user decides whether to act on any reported issues after the build completes.

### Phase 3: Stage

After the review report is shown to the user:

1. Stage all changes: `git add -A` in the worktree.
2. Commit with message: `build: step N - <step title>`.
3. Proceed to the next step.

## Completion

After all steps finish successfully:

1. Report the worktree path and branch name to the user.
2. Provide a build summary with:
   - Each step: name, type (scaffolding/code), test results (if code step), review outcome
   - A consolidated list of choices and assumptions made by agents across all steps. For each, state what the agent decided, why (if discernible), and which step it occurred in. This allows the user to course-correct anything that diverged from their intent.
3. Do not merge the branch or delete the worktree. The user decides what to do next.

## Constraints

- Follow the constraints listed in `commands/execute.md` and `commands/review.md`.
- Stop the entire build on any unresolved failure (execution or review). Do not skip steps.
- All work happens in the worktree, never in the original working directory.
