# Description Optimization

Methodology for optimizing a skill's description field for trigger accuracy. The description is the primary mechanism Claude uses to decide whether to load a skill.

## Step 1: Generate trigger eval queries

Create 20 eval queries -- a mix of should-trigger (8-10) and should-not-trigger (8-10). Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

### Query design rules

Queries must be realistic. Not abstract requests, but concrete prompts with detail: file paths, personal context, column names, company names. Some lowercase, some with abbreviations or typos or casual speech. Mix of lengths.

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

**Should-trigger queries (8-10):** Different phrasings of the same intent. Some formal, some casual. Include cases where the user does not explicitly name the skill or file type but clearly needs it. Include uncommon use cases and cases where this skill competes with another but should win.

**Should-not-trigger queries (8-10):** Near-misses. Queries that share keywords or concepts with the skill but need something different. Adjacent domains, ambiguous phrasing where a naive keyword match would trigger but should not. Do not make these obviously irrelevant -- "Write a fibonacci function" as a negative test for a PDF skill tests nothing.

### How skill triggering works

Skills appear in Claude's `available_skills` list with their name + description. Claude decides whether to consult a skill based on that description. Important: Claude only consults skills for tasks it cannot easily handle on its own. Simple, one-step queries like "read this PDF" may not trigger a skill even if the description matches perfectly, because Claude can handle them directly with basic tools. Complex, multi-step, or specialized queries reliably trigger skills when the description matches.

Eval queries should be substantive enough that Claude would benefit from consulting a skill. Simple queries are poor test cases.

## Step 2: Review with user

Present the eval set to the user. Let them edit queries, toggle should-trigger, add or remove entries. This step matters -- bad eval queries produce bad descriptions.

Save the reviewed eval set to the workspace.

## Step 3: Run the optimization loop

Run the optimization loop script:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from the current session so the triggering test matches what the user actually experiences.

### What the loop does

1. Splits the eval set into 60% train and 40% held-out test (stratified by should_trigger)
2. Evaluates the current description by running each query 3 times via `claude -p` to get a reliable trigger rate
3. Calls Claude to propose an improved description based on what failed
4. Re-evaluates the new description on both train and test
5. Iterates up to 5 times or until all train queries pass
6. Selects the best description by test score (not train score) to avoid overfitting

The loop produces an HTML report showing results per iteration and returns JSON with `best_description`.

## Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user the before/after descriptions and the test scores.

If the test score is lower than the train score by more than 20 percentage points, the description may be overfitting to the training queries. Consider expanding the eval set and running again.
