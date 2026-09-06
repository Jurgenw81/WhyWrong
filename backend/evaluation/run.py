from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .dataset import load_dataset
from .report import write_reports
from .runner import evaluate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate WhyWrong classification")
    parser.add_argument(
        "--provider", choices=("deterministic", "openai"), default="deterministic"
    )
    parser.add_argument(
        "--confirm-paid-run",
        action="store_true",
        help="Required for OpenAI runs because every dataset row creates a paid request.",
    )
    parser.add_argument("--limit", type=int, help="Evaluate only the first N examples")
    parser.add_argument(
        "--output", type=Path, default=Path("docs/evaluation-baseline.md")
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.provider == "openai" and not args.confirm_paid_run:
        raise SystemExit("OpenAI evaluation requires --confirm-paid-run")
    examples = load_dataset()
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be positive")
        examples = examples[: args.limit]
    summary = await evaluate(examples, provider=args.provider)
    markdown_path, json_path = write_reports(summary, args.provider, args.output)
    print(
        f"{args.provider}: {summary.accuracy:.1%} "
        f"({summary.passed}/{summary.total})"
    )
    print(f"Wrote {markdown_path} and {json_path}")


if __name__ == "__main__":
    asyncio.run(main())

