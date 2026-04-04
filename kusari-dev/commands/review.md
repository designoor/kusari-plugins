---
allowed-tools: Bash(gh pr view:*), Bash(gh pr list:*), Bash(gh pr diff:*)
description: Review uncommitted changes, optionally against an implementation step specification
argument-hint: "[step-file]"
disable-model-invocation: false
---

Review uncommitted code changes before commit. If a step file is provided, also check compliance against the step specification.

## Input

The user provided: `$ARGUMENTS`

This is an optional argument. If provided, it is either a file path or a filename pointing to an implementation step file.

- If no argument is provided, scan the current conversation for a prior `/execute` invocation. If one is found, use the filename or path from that invocation as the step file. If multiple `/execute` calls exist, use the most recent one. If none are found, proceed without a step file (review uncommitted changes only). When a step file is inferred this way, print the resolved path to the user (e.g., "Inferred step file: path/to/step-01-foo.md") before continuing.

- If it is a full path, read the file directly.
- If it is just a filename, search the current working directory and its subdirectories to locate it. If multiple matches are found, ask the user which one they mean. If no matches are found, tell the user and stop.
- If a step file is found, also find and read the sibling `index.md` in the same directory as the step file. This contains the implementation plan skeleton.

## Setup

1. Read `CLAUDE.md` from the current working directory if it exists. This contains project conventions.
2. If a step file was provided and located, read it and its sibling `index.md`.

To do this, follow these steps precisely:

1. Print the review target to the user before doing any work: "Reviewing: `<step-file-name>`" if a step file is being used, or "Reviewing: uncommitted changes" otherwise.
2. Run `git diff` and `git diff --cached` to collect unstaged and staged changes. Combine the output. If both are empty (no uncommitted changes), report that to the user and stop.
3. Use a Haiku agent to give you a list of file paths to (but not the contents of) any relevant CLAUDE.md files from the codebase: the root CLAUDE.md file (if one exists), as well as any CLAUDE.md files in the directories whose files appear in the diff
4. Use a Haiku agent to read the combined diff output, and ask the agent to return a summary of the change
5. Then, launch 5 parallel Sonnet agents (or 6, if a step file was provided) to independently code review the change. Each agent MUST return its findings using this exact format per issue (no deviations):

```
ISSUE:
title: <short generic label, max 8 words>
location: <file_path:line_number>
category: <one of: CLAUDE.md adherence | bug | historical context | PR context | code comment violation | spec compliance>
description: <2-3 sentences: what is wrong, why it matters, what to consider>
```

If the agent finds no issues, it returns `NO ISSUES FOUND`. Agents must report every potential issue they notice, even ones they suspect may be false positives. Do not self-filter. The scoring step (step 6) handles false-positive assessment. The agents:
   a. Agent #1: Audit the changes to make sure they comply with the CLAUDE.md. Note that CLAUDE.md is guidance for Claude as it writes code, so not all instructions will be applicable during code review.
   b. Agent #2: Read the file changes in the diff, then do a shallow scan for obvious bugs. Avoid reading extra context beyond the changes, focusing just on the changes themselves. Focus on large bugs, and avoid small issues and nitpicks. Ignore likely false positives.
   c. Agent #3: Read the git blame and history of the code modified, to identify any bugs in light of that historical context
   d. Agent #4: Read previous pull requests that touched these files, and check for any comments on those pull requests that may also apply to the current changes.
   e. Agent #5: Read code comments in the modified files, and make sure the changes in the diff comply with any guidance in the comments.
   f. Agent #6 (only if a step file was provided): Review the diff against the step file and sibling index.md. Check for: (a) missing functionality that the step specification requires, (b) changes that contradict the step specification, (c) changes outside the step's declared scope. Return issues in the same format as the other agents.
6. For each issue found in #5, launch a parallel Haiku agent that takes the diff, issue description, and list of CLAUDE.md files (from step 3), and returns a score to indicate the agent's level of confidence for whether the issue is real or false positive. To do that, the agent should score each issue on a scale from 0-100, indicating its level of confidence. For issues that were flagged due to CLAUDE.md instructions, the agent should double check that the CLAUDE.md actually calls out that issue specifically. Give each scoring agent the rubric AND the false-positive patterns below verbatim:

   Scoring rubric:
   a. 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny, or is a pre-existing issue.
   b. 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant CLAUDE.md.
   c. 50: Moderately confident. The agent was able to verify this is a real issue, but it might be a nitpick or not happen very often in practice. Relative to the rest of the diff, it's not very important.
   d. 75: Highly confident. The agent double checked the issue, and verified that it is very likely it is a real issue that will be hit in practice. The existing approach in the diff is insufficient. The issue is very important and will directly impact the code's functionality, or it is an issue that is directly mentioned in the relevant CLAUDE.md.
   e. 100: Absolutely certain. The agent double checked the issue, and confirmed that it is definitely a real issue, that will happen frequently in practice. The evidence directly confirms this.

   Patterns that should lower a score (give to scoring agents only, not review agents):
   - Pre-existing issues
   - Something that looks like a bug but is not actually a bug
   - Pedantic nitpicks that a senior engineer wouldn't call out
   - Issues that a linter, typechecker, or compiler would catch (eg. missing or incorrect imports, type errors, broken tests, formatting issues, pedantic style issues like newlines). These run separately.
   - General code quality issues (eg. lack of test coverage, general security issues, poor documentation), unless explicitly required in CLAUDE.md
   - Issues that are called out in CLAUDE.md, but explicitly silenced in the code (eg. due to a lint ignore comment)
   - Changes in functionality that are likely intentional or are directly related to the broader change
   - Real issues, but on lines that the user did not modify in their diff

7. Build the final report table. There is no score threshold. Every issue that was scored in step 6 appears in the table as its own row. Include issues scored 0, 25, 50, 75, and 100 alike. The score is informational for the user; it is not a filter. Do not summarize, collapse, or mention issues outside the table (e.g., "notable items below threshold" or "filtered out"). The table is the only output.

Notes:

- Do not check build signal or attempt to build or typecheck the app. These will run separately, and are not relevant to your code review.
- Make a todo list first
- Cite each issue with file path and line number (eg. if referring to a CLAUDE.md, cite it with its path)
- Keep output brief, no emojis, use `file_path:line_number` references
- For your final report, follow this table format precisely. Do not use any other layout:

---

### Code review: `<step-file-name or "uncommitted changes">`

Found N issues:

| # | Issue | Score | Location | Details |
|---|-------|-------|----------|---------|
| 1 | <short label, max 8 words> | <0-100> | `file:line` | <what is wrong, why it matters, max 120 chars> |
| 2 | ... | ... | ... | ... |
| ... (one row per issue, no omissions) | | | | |
| N | ... | ... | ... | ... |

---

- If every agent returned `NO ISSUES FOUND` (zero issues across all agents, before scoring):

---

### Code review: `<step-file-name or "uncommitted changes">`

No issues found. Checked for bugs and CLAUDE.md compliance.

---

- If any agent reported at least one issue, use the table. Never use "No issues found" when issues exist, even if all scores are 0.
- Sort by score descending (highest first).
- The "Issue" column is the short label. "Details" carries the explanation. Keep Details under 120 characters.
- Do not merge, omit, collapse, or summarize rows. Do not mention issues in prose outside the table. Every issue gets its own row in the table or it is missing.