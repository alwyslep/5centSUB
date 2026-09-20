"""Command-line interface for offline contract validation."""

import argparse
from decimal import Decimal
import json
from pathlib import Path
from typing import Sequence

from .budget import BudgetLedger
from .pipeline import SubtitlePipeline
from .providers import MockTranscriptProvider, MockTranslationProvider
from .srt import parse_srt


_JAPANESE_SRT = """1
00:00:00,000 --> 00:00:02,000
こんにちは。

2
00:00:02,500 --> 00:00:04,500
今日はいい天気ですね。
"""

_KOREAN_SRT = """1
00:00:00,000 --> 00:00:02,000
안녕하세요.

2
00:00:02,500 --> 00:00:04,500
오늘 날씨가 좋네요.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="5centsub")
    subcommands = parser.add_subparsers(dest="command", required=True)

    demo = subcommands.add_parser("demo", help="run an offline mock subtitle job")
    demo.add_argument("--budget-usd", type=Decimal, default=Decimal("0.05"))

    validate = subcommands.add_parser("validate-srt", help="validate an SRT file")
    validate.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-srt":
        cues = parse_srt(args.path.read_text(encoding="utf-8-sig"))
        print(json.dumps({"valid": True, "cues": len(cues)}, ensure_ascii=False))
        return 0

    pipeline = SubtitlePipeline(
        MockTranscriptProvider(_JAPANESE_SRT),
        MockTranslationProvider(_KOREAN_SRT),
    )
    result = pipeline.run("mock://authorized-sample", BudgetLedger(args.budget_usd))
    print(
        json.dumps(
            {
                "stage": result.stage.value,
                "stage_history": [stage.value for stage in result.stage_history],
                "actual_cost_usd": result.actual_cost_usd,
                "failure_reason": result.failure_reason,
                "korean_srt": result.korean_srt,
            },
            ensure_ascii=False,
        )
    )
    return 0 if result.stage.value == "completed" else 1
