---
allowed-tools: Bash(gh pr view:*), Bash(gh pr list:*), Bash(gh pr diff:*)
description: Review uncommitted changes using the review agent, optionally against a step spec
argument-hint: "[step-file]"
disable-model-invocation: false
---

Launch the `review` agent with `$ARGUMENTS` as the step file path. If no argument was provided, instruct the agent to collect the diff from uncommitted changes without a step file.
