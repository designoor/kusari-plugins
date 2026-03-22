---
description: Execute a single implementation plan step by generating tests first, then code, with automatic test validation and retry
argument-hint: <path-or-filename>
disable-model-invocation: false
---

You are orchestrating the execution of a single implementation plan step.

## Input

The user provided: `$ARGUMENTS`

This is either a file path or a filename. If it is a full path, read the file directly. If it is just a filename, search the current working directory and its subdirectories to locate it. If multiple matches are found, ask the user which one they mean. If no matches are found, tell the user and stop.

## Setup

1. Read the step file.
2. Find and read the sibling `index.md` in the same directory as the step file. This contains the implementation plan skeleton.
3. Read `CLAUDE.md` from the current working directory if it exists. This contains project conventions.
4. Detect the step type by checking for the classification tag in `index.md`: `[scaffolding]` or `[code]`. If neither tag is present, classify based on content: if the step has no Interfaces and no Functions/Methods sections (or they say "None"), it is scaffolding. Otherwise, it is code.

## Execution: Scaffolding Steps

1. Launch the `implementer` agent. Pass it:
   - The step file contents
   - The index file contents
   - The CLAUDE.md contents (if present)
   - Step type: "scaffolding"

2. After the implementer finishes, run the Post-Setup Verification commands listed in the step file. Run each command and check the output against the expected result described in the step.

3. If any verification command fails, pass the failure output to the `implementer` agent and ask it to fix. Retry up to 3 times total.

4. Report results to the user. List the verification command outcomes.

## Execution: Code Steps

1. Launch the `test-writer` agent. Pass it:
   - The step file contents
   - The index file contents
   - The CLAUDE.md contents (if present)

2. After test-writer finishes, launch the `implementer` agent. Pass it:
   - The step file contents
   - The index file contents
   - The CLAUDE.md contents (if present)
   - Step type: "code"

3. After the implementer finishes, detect the project's test runner and run the tests.

4. If tests fail, pass the failure output (stderr and stdout) to the `implementer` agent and ask it to fix the production code. Do not modify test files. Retry up to 3 times total.

5. After exhausting retries with tests still failing, report the remaining failures to the user and stop.

6. Report results to the user. Include:
   - What was implemented
   - Test results (pass/fail counts)
   - The Acceptance Criteria from the step file as a checklist for the user to review

## Constraints

- Never skip the test-writer for code steps. Tests are written first, always.
- Never modify test files during the retry loop. Only production code gets fixed.
- The implementer must not add functionality beyond what the step specifies.
