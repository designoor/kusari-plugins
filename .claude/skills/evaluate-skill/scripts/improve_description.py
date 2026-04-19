#!/usr/bin/env python3
"""Improve a skill description based on eval results.

Calls `claude -p` as a subprocess to generate an improved description
based on what failed in the trigger evaluation.

Adapted from anthropics/skills skill-creator.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from scripts.utils import parse_skill_md


def _call_claude(prompt: str, model: str | None, timeout: int = 300) -> str:
    """Run `claude -p` with the prompt on stdin and return the text response."""
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p exited {result.returncode}\nstderr: {result.stderr}"
        )
    return result.stdout


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    model: str,
    log_dir: Path | None = None,
    iteration: int | None = None,
) -> str:
    """Call Claude to improve the description based on eval results."""
    failed = [r for r in eval_results["results"] if not r["pass"]]
    passed = [r for r in eval_results["results"] if r["pass"]]

    failed_lines = []
    for r in failed:
        expected = "trigger" if r["should_trigger"] else "not trigger"
        actual_rate = f"{r['triggers']}/{r['runs']}"
        failed_lines.append(
            f"  FAILED: \"{r['query'][:100]}\" "
            f"(expected {expected}, trigger rate {actual_rate})"
        )

    passed_lines = []
    for r in passed:
        expected = "trigger" if r["should_trigger"] else "not trigger"
        actual_rate = f"{r['triggers']}/{r['runs']}"
        passed_lines.append(
            f"  PASSED: \"{r['query'][:100]}\" "
            f"(expected {expected}, trigger rate {actual_rate})"
        )

    history_text = ""
    if history:
        history_text = "\n\nPrevious attempts:\n"
        for h in history:
            history_text += (
                f"  Iteration {h['iteration']}: "
                f"{h['passed']}/{h['total']} passed "
                f"| Description: \"{h['description'][:120]}...\"\n"
            )

    prompt = f"""You are optimizing a skill description for trigger accuracy.

The skill "{skill_name}" has this description:
"{current_description}"

Here is the skill content (for context on what it does):
{skill_content[:3000]}

Eval results:
{chr(10).join(failed_lines)}
{chr(10).join(passed_lines)}
{history_text}

Your task: write an improved description that fixes the failures without breaking what already passes.

Rules:
- The description determines whether Claude loads the skill for a given query
- Include specific trigger phrases and contexts
- Include negative triggers ("Do NOT use when...") to prevent false positives
- Keep it under 1024 characters
- Do not add filler or marketing language
- Focus on what the skill DOES and WHEN to use it

Return ONLY the new description text, nothing else. No quotes, no explanation."""

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"improve_iteration_{iteration or 'unknown'}.txt"
        log_file.write_text(f"PROMPT:\n{prompt}\n\n")

    response = _call_claude(prompt, model)
    new_description = response.strip().strip('"').strip("'")

    if log_dir and iteration:
        log_file = log_dir / f"improve_iteration_{iteration}.txt"
        with open(log_file, "a") as f:
            f.write(f"RESPONSE:\n{new_description}\n")

    return new_description


def main():
    parser = argparse.ArgumentParser(
        description="Improve a skill description based on eval results"
    )
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--eval-results", required=True, help="Path to eval results JSON")
    parser.add_argument("--model", required=True, help="Model for improvement")
    parser.add_argument("--history", default=None, help="Path to history JSON")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    name, description, content = parse_skill_md(skill_path)
    eval_results = json.loads(Path(args.eval_results).read_text())
    history = json.loads(Path(args.history).read_text()) if args.history else []

    new_description = improve_description(
        skill_name=name,
        skill_content=content,
        current_description=description,
        eval_results=eval_results,
        history=history,
        model=args.model,
    )

    print(new_description)


if __name__ == "__main__":
    main()
