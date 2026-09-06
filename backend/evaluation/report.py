from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .metrics import EvaluationSummary


def render_markdown(summary: EvaluationSummary, provider: str) -> str:
    lines = [
        "# WhyWrong classifier evaluation",
        "",
        f"- Provider: `{provider}`",
        f"- Evaluated: {datetime.now(UTC).date().isoformat()}",
        f"- Examples: {summary.total}",
        f"- Overall accuracy: **{summary.accuracy:.1%}** ({summary.passed}/{summary.total})",
        "",
        "## Results by label",
        "",
        "| Expected label | Passed | Total | Accuracy |",
        "|---|---:|---:|---:|",
    ]
    for label, metrics in summary.per_label.items():
        lines.append(
            f"| `{label}` | {metrics['passed']} | {metrics['total']} | "
            f"{float(metrics['accuracy']):.1%} |"
        )

    failures = [result for result in summary.results if not result.passed]
    lines.extend(["", "## Errors", ""])
    if failures:
        lines.extend(
            [
                "| Example | Expected | Predicted |",
                "|---|---|---|",
                *[
                    f"| `{item.example_id}` | `{item.expected}` | `{item.predicted}` |"
                    for item in failures
                ],
            ]
        )
    else:
        lines.append("No errors in this run.")
    lines.extend(
        [
            "",
            "## Method",
            "",
            "Correct answers must pass without diagnosis. Known misconception examples "
            "must rank the matching hypothesis first with a decisive margin. Ambiguous "
            "answers pass when the system asks a diagnostic probe instead of claiming "
            "the answer is correct.",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(
    summary: EvaluationSummary, provider: str, markdown_path: Path
) -> tuple[Path, Path]:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(summary, provider), encoding="utf-8")
    json_path = markdown_path.with_suffix(".json")
    json_path.write_text(
        json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8"
    )
    return markdown_path, json_path

