#!/usr/bin/env python3
"""Generate an HTML report from run_loop.py output.

Takes the JSON output from run_loop.py and generates a visual HTML report
showing each description attempt with pass/fail for each test case.
Distinguishes between train and test queries.

Adapted from anthropics/skills skill-creator.
"""

import argparse
import html
import json
import sys
from pathlib import Path


def generate_html(
    data: dict, auto_refresh: bool = False, skill_name: str = ""
) -> str:
    """Generate HTML report from loop output data."""
    history = data.get("history", [])
    holdout = data.get("holdout", 0)
    title_prefix = html.escape(skill_name + " - ") if skill_name else ""

    train_queries: list[dict] = []
    test_queries: list[dict] = []
    if history:
        for r in history[0].get("train_results", history[0].get("results", [])):
            train_queries.append({
                "query": r["query"],
                "should_trigger": r.get("should_trigger", True),
            })
        if history[0].get("test_results"):
            for r in history[0].get("test_results", []):
                test_queries.append({
                    "query": r["query"],
                    "should_trigger": r.get("should_trigger", True),
                })

    refresh_tag = (
        '    <meta http-equiv="refresh" content="5">\n' if auto_refresh else ""
    )

    rows_html = ""
    for h in history:
        iteration = h["iteration"]
        desc = html.escape(h["description"])
        train_passed = h.get("train_passed", h.get("passed", 0))
        train_total = h.get("train_total", h.get("total", 0))
        test_passed = h.get("test_passed")
        test_total = h.get("test_total")

        train_results = h.get("train_results", h.get("results", []))
        test_results_list = h.get("test_results", [])

        train_cells = ""
        for q in train_queries:
            matching = [
                r for r in train_results if r["query"] == q["query"]
            ]
            if matching:
                r = matching[0]
                passed = r["pass"]
                rate = f"{r['triggers']}/{r['runs']}"
                color = "#2d5" if passed else "#f44"
                symbol = "P" if passed else "F"
                train_cells += (
                    f'<td style="background:{color};color:#fff;text-align:center" '
                    f'title="{html.escape(q["query"][:80])}\n'
                    f'rate: {rate}">{symbol}</td>'
                )
            else:
                train_cells += '<td style="background:#888;text-align:center">?</td>'

        test_cells = ""
        for q in test_queries:
            matching = [
                r for r in test_results_list if r["query"] == q["query"]
            ]
            if matching:
                r = matching[0]
                passed = r["pass"]
                rate = f"{r['triggers']}/{r['runs']}"
                color = "#2d5" if passed else "#f44"
                symbol = "P" if passed else "F"
                test_cells += (
                    f'<td style="background:{color};color:#fff;text-align:center" '
                    f'title="{html.escape(q["query"][:80])}\n'
                    f'rate: {rate}">{symbol}</td>'
                )
            else:
                test_cells += '<td style="background:#888;text-align:center">?</td>'

        score_text = f"{train_passed}/{train_total}"
        if test_passed is not None:
            score_text += f" (test: {test_passed}/{test_total})"

        rows_html += (
            f"<tr>"
            f"<td>{iteration}</td>"
            f'<td style="max-width:400px;overflow:hidden;text-overflow:ellipsis;'
            f'white-space:nowrap" title="{desc}">{desc}</td>'
            f"<td>{score_text}</td>"
            f"{train_cells}"
            f"{test_cells}"
            f"</tr>\n"
        )

    train_headers = ""
    for i, q in enumerate(train_queries):
        label = "T+" if q["should_trigger"] else "T-"
        train_headers += (
            f'<th title="{html.escape(q["query"][:80])}" '
            f'style="writing-mode:vertical-lr;min-width:30px">{label}{i+1}</th>'
        )

    test_headers = ""
    for i, q in enumerate(test_queries):
        label = "H+" if q["should_trigger"] else "H-"
        test_headers += (
            f'<th title="{html.escape(q["query"][:80])}" '
            f'style="writing-mode:vertical-lr;min-width:30px">{label}{i+1}</th>'
        )

    best_desc = html.escape(data.get("best_description", ""))
    best_score = data.get("best_score", "")

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
{refresh_tag}    <title>{title_prefix}Description Optimization Report</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2em; background: #1a1a2e; color: #e0e0e0; }}
        h1 {{ color: #fff; }}
        table {{ border-collapse: collapse; margin: 1em 0; }}
        th, td {{ border: 1px solid #333; padding: 6px 10px; }}
        th {{ background: #16213e; }}
        .best {{ background: #0f3460; padding: 1em; border-radius: 8px; margin: 1em 0; }}
        .best h3 {{ margin-top: 0; color: #4cc9f0; }}
    </style>
</head>
<body>
    <h1>{title_prefix}Description Optimization Report</h1>

    <div class="best">
        <h3>Best Description (score: {best_score})</h3>
        <p>{best_desc}</p>
    </div>

    <table>
        <thead>
            <tr>
                <th>Iter</th>
                <th>Description</th>
                <th>Score</th>
                {train_headers}
                {test_headers}
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <p style="color:#888">
        T+ = train should-trigger, T- = train should-not-trigger,
        H+ = holdout should-trigger, H- = holdout should-not-trigger.
        Hover cells for query text and trigger rate.
    </p>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML report from optimization loop results"
    )
    parser.add_argument("results_json", type=Path, help="Path to results.json")
    parser.add_argument("--output", "-o", type=Path, help="Output HTML path")
    parser.add_argument("--skill-name", default="", help="Skill name for title")
    args = parser.parse_args()

    data = json.loads(args.results_json.read_text())
    output_path = args.output or args.results_json.with_suffix(".html")

    report_html = generate_html(data, skill_name=args.skill_name)
    output_path.write_text(report_html)
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()
