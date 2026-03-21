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

- If it is a full path, read the file directly.
- If it is just a filename, search the current working directory and its subdirectories to locate it. If multiple matches are found, ask the user which one they mean. If no matches are found, tell the user and stop.
- If a step file is found, also find and read the sibling `index.md` in the same directory as the step file. This contains the implementation plan skeleton.

## Setup

1. Read `CLAUDE.md` from the current working directory if it exists. This contains project conventions.
2. If a step file was provided and located, read it and its sibling `index.md`.

To do this, follow these steps precisely:

1. Run `git diff` and `git diff --cached` to collect unstaged and staged changes. Combine the output. If both are empty (no uncommitted changes), report that to the user and stop.
2. Use a Haiku agent to give you a list of file paths to (but not the contents of) any relevant CLAUDE.md files from the codebase: the root CLAUDE.md file (if one exists), as well as any CLAUDE.md files in the directories whose files appear in the diff
3. Use a Haiku agent to read the combined diff output, and ask the agent to return a summary of the change
4. Then, launch 5 parallel Sonnet agents (or 6, if a step file was provided) to independently code review the change. The agents should do the following, then return a list of issues and the reason each issue was flagged (eg. CLAUDE.md adherence, bug, historical git context, etc.):
   a. Agent #1: Audit the changes to make sure they comply with the CLAUDE.md. Note that CLAUDE.md is guidance for Claude as it writes code, so not all instructions will be applicable during code review.
   b. Agent #2: Read the file changes in the diff, then do a shallow scan for obvious bugs. Avoid reading extra context beyond the changes, focusing just on the changes themselves. Focus on large bugs, and avoid small issues and nitpicks. Ignore likely false positives.
   c. Agent #3: Read the git blame and history of the code modified, to identify any bugs in light of that historical context
   d. Agent #4: Read previous pull requests that touched these files, and check for any comments on those pull requests that may also apply to the current changes.
   e. Agent #5: Read code comments in the modified files, and make sure the changes in the diff comply with any guidance in the comments.
   f. Agent #6 (only if a step file was provided): Review the diff against the step file and sibling index.md. Check for: (a) missing functionality that the step specification requires, (b) changes that contradict the step specification, (c) changes outside the step's declared scope. Return issues in the same format as the other agents.
5. For each issue found in #4, launch a parallel Haiku agent that takes the diff, issue description, and list of CLAUDE.md files (from step 2), and returns a score to indicate the agent's level of confidence for whether the issue is real or false positive. To do that, the agent should score each issue on a scale from 0-100, indicating its level of confidence. For issues that were flagged due to CLAUDE.md instructions, the agent should double check that the CLAUDE.md actually calls out that issue specifically. The scale is (give this rubric to the agent verbatim):
   a. 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny, or is a pre-existing issue.
   b. 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant CLAUDE.md.
   c. 50: Moderately confident. The agent was able to verify this is a real issue, but it might be a nitpick or not happen very often in practice. Relative to the rest of the diff, it's not very important.
   d. 75: Highly confident. The agent double checked the issue, and verified that it is very likely it is a real issue that will be hit in practice. The existing approach in the diff is insufficient. The issue is very important and will directly impact the code's functionality, or it is an issue that is directly mentioned in the relevant CLAUDE.md.
   e. 100: Absolutely certain. The agent double checked the issue, and confirmed that it is definitely a real issue, that will happen frequently in practice. The evidence directly confirms this.
6. Filter out any issues with a score less than 80. If there are no issues that meet this criteria, do not proceed.
7. Report the review results directly to the user. When writing your report, keep in mind to:
   a. Keep your output brief
   b. Avoid emojis
   c. Cite relevant code using `file_path:line_number` references

Examples of false positives, for steps 4 and 5:

- Pre-existing issues
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that a linter, typechecker, or compiler would catch (eg. missing or incorrect imports, type errors, broken tests, formatting issues, pedantic style issues like newlines). No need to run these build steps yourself -- it is safe to assume that they will be run separately as a separate step.
- General code quality issues (eg. lack of test coverage, general security issues, poor documentation), unless explicitly required in CLAUDE.md
- Issues that are called out in CLAUDE.md, but explicitly silenced in the code (eg. due to a lint ignore comment)
- Changes in functionality that are likely intentional or are directly related to the broader change
- Real issues, but on lines that the user did not modify in their diff

Notes:

- Do not check build signal or attempt to build or typecheck the app. These will run separately, and are not relevant to your code review.
- Make a todo list first
- You must cite each bug with a file path and line number (eg. if referring to a CLAUDE.md, cite it with its path)
- For your final report, follow the following format precisely (assuming for this example that you found 3 issues):

---

### Code review

Found 3 issues:

1. <brief description of bug> (CLAUDE.md says "<...>")

   `src/foo/bar.ts:42`

2. <brief description of bug> (some/other/CLAUDE.md says "<...>")

   `src/baz/qux.py:17`

3. <brief description of bug> (bug due to <file and code snippet>)

   `lib/thing.go:88`

---

- Or, if you found no issues:

---

### Code review

No issues found. Checked for bugs and CLAUDE.md compliance.

- When citing code, use `file_path:line_number` format (e.g. `src/utils/parse.ts:42`). Provide enough context for the user to locate the issue.
