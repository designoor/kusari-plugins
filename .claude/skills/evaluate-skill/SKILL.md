---
name: evaluate-skill
description: Test, measure, and iteratively improve Claude Code skills. Use when the user wants to test a skill, run evals, benchmark skill performance, compare two skill versions, optimize a skill's description for better triggering accuracy, or measure whether a skill provides value over baseline Also use when the user says "evaluate my skill", "test this skill", "is my skill working", "improve triggering", "compare these skills", or "run evals".
argument-hint: "[path-to-skill]"
---

# Evaluate Skill

Test, measure, and iteratively improve Claude Code skills through structured evaluation.

## Phase 0: Detect and Route

### 0.1 Identify the skill under test

If `$ARGUMENTS` contains a path, use it. Otherwise check the current conversation for a skill path mentioned earlier. If neither, ask:

> Which skill do you want to evaluate? Provide the path to the skill directory.

Verify the path contains a SKILL.md. If not, stop.

### 0.1b Select model and effort

Ask the user which model and effort level to use for the evaluation runs:

> Which model should the eval runs use? (e.g. `sonnet`, `opus`, `haiku`, or a specific model ID)
>
> What effort level? (`low`, `medium`, `high`, `xhigh`, `max`, or skip for default)

Use the selected model and effort when spawning subagents in Phase 2. Record both in `eval_metadata.json` and the report metadata. If the user skips effort, omit it (use the model's default).

### 0.2 Detect existing workspace

The evaluation workspace lives at `<project-root>/.claude/evaluation/<skill-name>/`. Look for this directory. If it exists, check for `evals.json` and `iteration-*/` subdirectories.

| State | Signal |
|---|---|
| No workspace | First evaluation. Proceed to Phase 1. |
| Workspace with iterations | Prior work exists. Offer to continue from the latest iteration (skip to Phase 4 to review, or Phase 5 to improve) or start fresh. |
| Workspace with `feedback.json` in latest iteration | User reviewed but improvement not yet applied. Skip to Phase 5. |

### 0.3 Classify entry point

Determine intent from the user's request:

| Intent | Route |
|---|---|
| Test and evaluate a skill | Phase 1 |
| Continue iterating on prior results | Phase 4 or 5 (per 0.2) |
| Optimize description / fix triggering | Phase 6 |
| Compare two skill versions | Phase 1, with both versions as test targets |

### 0.4 Classify skill value type

Read the skill's SKILL.md and classify:

**Capability uplift** -- the skill teaches techniques the base model cannot reliably produce on its own. Testing must compare with-skill vs without-skill to prove the skill adds value. Examples: file format skills, API-specific knowledge, creative techniques.

**Encoded preference** -- the skill sequences steps the model can already handle individually. Testing focuses on whether the workflow produces consistent, correctly-ordered output. Baseline comparison is less meaningful since the model can do each step; the value is in the orchestration. Examples: debug workflows, planning procedures.

This classification affects how Phase 2 baselines are configured and how Phase 3 results are interpreted.

## Phase 1: Design Test Prompts

### 1.1 Create test prompts

Design 3-5 realistic test prompts. Each prompt should be something a real user would type, with enough specificity to produce a meaningful output.

Qualities of good test prompts:
- Concrete: include file paths, column names, personal context, specific details
- Varied: mix lengths, formality levels, edge cases
- Representative: cover the skill's core use cases and at least one boundary case

Bad: "Format this data"
Good: "I have a CSV in ~/reports/q4-sales.csv with columns for region, revenue, and headcount. Can you make a chart showing revenue per region?"

### 1.2 Classify test approach

Based on the skill value type from Phase 0.4:

| Value type | Baseline | What to measure |
|---|---|---|
| Capability uplift | Without skill (same prompt, no skill loaded) | Does the skill enable output the model cannot produce alone? |
| Encoded preference | Without skill, OR no baseline | Does the skill produce consistent, correctly-sequenced output? |

For capability uplift, always run a without-skill baseline. For encoded preference, a baseline is optional but useful for measuring consistency improvement.

### 1.3 Draft assertions

For each test prompt, draft 2-4 quantitative assertions. Assertions must be objectively verifiable.

Good assertions:
- "Output file exists and is valid XLSX" (programmatically checkable)
- "Chart contains exactly 3 data series" (inspectable)
- "Response includes SQL query before executing it" (pattern match)

Bad assertions:
- "Output looks professional" (subjective)
- "Code is well-structured" (unmeasurable)

### 1.4 Save test cases

Check if `<project-root>/.claude/evaluation/<skill-name>/evals.json` already exists. If it does, read it and present the existing test cases to the user. Ask whether to use them as-is, modify them, or generate new ones.

If no evals.json exists, save to `<project-root>/.claude/evaluation/<skill-name>/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "assertions": [
        "Output file exists at the specified path",
        "File contains at least 3 sections"
      ],
      "files": []
    }
  ]
}
```

Present the test prompts and assertions to the user for review before proceeding.

## Phase 2: Run Tests

### 2.1 Create workspace

Create `<project-root>/.claude/evaluation/<skill-name>/iteration-<N>/` for the current iteration. The evals.json lives at the skill-name level; iteration directories are nested under it.

### 2.2 Spawn all runs in one turn

For each test prompt, spawn two subagents in the same turn:

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any>
- Save outputs to: <evaluation-dir>/iteration-<N>/eval-<ID>/with_skill/run-1/outputs/
```

**Baseline run** (for capability uplift skills):
```
Execute this task (no skill):
- Task: <eval prompt>
- Input files: <eval files if any>
- Save outputs to: <evaluation-dir>/iteration-<N>/eval-<ID>/without_skill/run-1/outputs/
```

The `run-1/` subdirectory inside each config is required. The aggregation script scans for `run-*` directories to collect results. For multiple runs of the same eval, use `run-2/`, `run-3/`, etc.

Launch all runs (with-skill + baseline for every test case) in the same turn. Do not wait for with-skill runs to finish before spawning baselines.

Write an `eval_metadata.json` for each test case in the eval directory (not inside run-1/):
```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": ["assertion 1", "assertion 2"],
  "model": "<model-id-powering-this-session>",
  "timestamp": "<ISO-8601 timestamp>"
}
```

### 2.3 Capture timing data

When each subagent task completes, the notification contains `total_tokens` and `duration_ms`. Save immediately to `timing.json` in the `run-1/` directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This data is only available in the task notification. Capture it as each notification arrives.

## Phase 3: Grade and Benchmark

### 3.1 Grade each run

For each completed run, dispatch the grader agent (`${CLAUDE_SKILL_DIR}/agents/grader.md`). The grader evaluates every assertion against the outputs and saves `grading.json` in the `run-1/` directory (alongside `timing.json` and `outputs/`).

For assertions that can be checked programmatically (file exists, contains N items, matches pattern), write and run a script rather than relying on the grader's judgment. Scripts are faster, more reliable, and reusable across iterations.

The `grading.json` expectations array must use the fields `text`, `passed`, and `evidence`. The aggregation script depends on these exact field names.

### 3.2 Aggregate benchmark

Run the aggregation script:
```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-<N> --skill-name <name>
```

This produces `benchmark.json` and `benchmark.md` with:
- Pass rate, time, and tokens for each configuration
- Mean, stddev, min, max per metric
- Delta between with-skill and baseline

### 3.3 Analyze patterns

Dispatch the analyzer agent (`${CLAUDE_SKILL_DIR}/agents/analyzer.md`) to read the benchmark data and surface patterns the aggregate stats might hide:
- Assertions that always pass regardless of skill (non-discriminating)
- High-variance evals (possibly flaky)
- Time/token tradeoffs
- Per-assertion and cross-eval patterns

The analyzer writes observations to `analysis.json` in the iteration directory.

## Phase 4: Review with User

### 4.1 Generate the eval report

Read the HTML template from `${CLAUDE_SKILL_DIR}/assets/eval-report-template.html`. Build a JSON object with this structure:

```json
{
  "metadata": {
    "skill_name": "example-skill",
    "model": "<model-id-powering-this-session>",
    "timestamp": "<ISO-8601 timestamp>"
  },
  "evals": [
    {
      "eval_id": 0,
      "eval_name": "descriptive-name",
      "prompt": "the test prompt",
      "configs": [
        {
          "config_name": "with_skill",
          "output_files": ["outputs/report.xlsx"],
          "timing": {"total_tokens": 84852, "total_duration_seconds": 23.3},
          "expectations": [
            {"text": "assertion text", "passed": true, "evidence": "why"}
          ]
        },
        {
          "config_name": "without_skill",
          "output_files": ["outputs/report.xlsx"],
          "timing": {"total_tokens": 42000, "total_duration_seconds": 12.1},
          "expectations": [
            {"text": "assertion text", "passed": false, "evidence": "why not"}
          ]
        }
      ]
    }
  ],
  "benchmark": {},
  "analysis": {}
}
```

Populate `benchmark` from `benchmark.json` and `analysis` from `analysis.json`. Populate each eval's configs from the corresponding `grading.json` and `timing.json` files.

In the template, replace:
- `__SKILL_NAME__` with the skill name
- `__ITERATION__` with the iteration number
- `__REPORT_DATA__` with the JSON object (no quotes -- it is a JS variable assignment)

Write the result to `<evaluation-dir>/iteration-<N>/eval-report.html`. Tell the user the path so they can open it in their browser.

### 4.2 Collect feedback

The report has an "Export Feedback" button that downloads `feedback.json`. When the user tells you they are done reviewing, read `feedback.json` from their downloads or from the workspace directory.

Empty feedback on a test case means it looked fine. Focus improvement effort on test cases where the user has specific complaints.

If the user is satisfied with all results, the evaluation is complete. Otherwise, proceed to Phase 5.

## Phase 5: Improve and Iterate

### 5.1 Analyze feedback

Read the user's feedback alongside the grading results and analyzer observations. Identify:
- Which test cases failed or received negative feedback
- Whether failures are specific to individual cases or systemic
- Whether the skill's instructions caused the model to waste effort (read transcripts, not just outputs)

### 5.2 Improve the skill

Apply changes to the skill. Guidelines:

**Generalize, do not overfit.** The test cases are a sample. Changes that fix one test case but would break others are harmful. If a stubborn issue persists, try different approaches rather than adding rigid constraints.

**Keep the skill lean.** If the model wastes time on unproductive steps, remove the instructions causing it. Read the transcripts to identify these.

**Explain the why.** Constraints with rationale outperform constraints with emphasis. "NEVER do X because it causes Y" is stronger than "NEVER do X" alone.

**Look for repeated work.** If every test run independently wrote a similar helper script or took the same multi-step approach, the skill should bundle that script in scripts/.

### 5.3 Rerun

After improving the skill, return to Phase 2. Run all test cases into a new `iteration-<N+1>/` directory.

For capability uplift skills, the baseline is always without-skill. For encoded preference skills, use judgment: baseline against the previous iteration or the original version.

### 5.4 Loop exit

Stop iterating when:
- The user says they are satisfied
- All assertions pass and feedback is empty
- Improvements are no longer producing meaningful change

## Phase 6: Description Optimization

This phase optimizes the skill's description for trigger accuracy. Accessible directly from Phase 0 when the user's goal is trigger improvement, or after Phase 5 when the skill content is stable.

Read `references/description-optimization.md` for the full methodology: designing trigger eval queries, the train/test split approach, running the optimization loop, and applying results.
