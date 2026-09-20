"""Command-line interface for offline contract validation."""

import argparse
from decimal import Decimal
import json
from pathlib import Path
from typing import Sequence

from .budget import BudgetLedger
from .estimation import RateCard, UsageEstimate, estimate_cost
from .media import build_audio_extraction_command, prepare_audio
from .pipeline import SubtitlePipeline
from .providers import MockTranscriptProvider, MockTranslationProvider
from .ass import parse_ass


_ASS_HEADER = """[Script Info]
Title: 5centSUB mock subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000019FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

_JAPANESE_ASS = (
    _ASS_HEADER
    + """Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,こんにちは。
Dialogue: 0,0:00:02.50,0:00:04.50,Default,,0,0,0,,今日はいい天気ですね。
"""
)

_KOREAN_ASS = (
    _ASS_HEADER
    + """Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,안녕하세요.
Dialogue: 0,0:00:02.50,0:00:04.50,Default,,0,0,0,,오늘 날씨가 좋네요.
"""
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="5centsub")
    subcommands = parser.add_subparsers(dest="command", required=True)

    demo = subcommands.add_parser("demo", help="run an offline mock subtitle job")
    demo.add_argument("--budget-usd", type=Decimal, default=Decimal("0.05"))

    validate = subcommands.add_parser("validate-ass", help="validate an ASS file")
    validate.add_argument("path", type=Path)

    estimate = subcommands.add_parser("estimate", help="estimate a cloud job from measured usage")
    estimate.add_argument("--source-seconds", type=Decimal, required=True)
    estimate.add_argument("--speech-seconds", type=Decimal, required=True)
    estimate.add_argument("--audio-tokens-per-second", type=Decimal, required=True)
    estimate.add_argument("--asr-input-usd-per-million", type=Decimal, required=True)
    estimate.add_argument("--asr-output-tokens", type=Decimal, required=True)
    estimate.add_argument("--asr-output-usd-per-million", type=Decimal, required=True)
    estimate.add_argument("--translation-input-tokens", type=Decimal, required=True)
    estimate.add_argument("--translation-input-usd-per-million", type=Decimal, required=True)
    estimate.add_argument("--translation-output-tokens", type=Decimal, required=True)
    estimate.add_argument("--translation-output-usd-per-million", type=Decimal, required=True)
    estimate.add_argument("--budget-usd", type=Decimal, default=Decimal("0.05"))

    prepare = subcommands.add_parser("prepare-audio", help="extract 16 kHz mono FLAC with FFmpeg")
    prepare.add_argument("input_media", type=Path)
    prepare.add_argument("output_audio", type=Path)
    prepare.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-ass":
        cues = parse_ass(args.path.read_text(encoding="utf-8-sig"))
        print(json.dumps({"valid": True, "cues": len(cues)}, ensure_ascii=False))
        return 0
    if args.command == "estimate":
        usage = UsageEstimate(
            args.source_seconds,
            args.speech_seconds,
            args.audio_tokens_per_second,
            args.asr_output_tokens,
            args.translation_input_tokens,
            args.translation_output_tokens,
        )
        rates = RateCard(
            args.asr_input_usd_per_million,
            args.asr_output_usd_per_million,
            args.translation_input_usd_per_million,
            args.translation_output_usd_per_million,
        )
        estimate = estimate_cost(usage, rates)
        budget = BudgetLedger(args.budget_usd)
        print(
            json.dumps(
                {
                    "source_seconds": str(usage.source_seconds),
                    "speech_seconds": str(usage.speech_seconds),
                    "speech_ratio": str(usage.speech_ratio.quantize(Decimal("0.000001"))),
                    "asr_input_tokens": str(usage.asr_input_tokens),
                    "costs_usd": {
                        "asr_input": str(estimate.asr_input_usd),
                        "asr_output": str(estimate.asr_output_usd),
                        "translation_input": str(estimate.translation_input_usd),
                        "translation_output": str(estimate.translation_output_usd),
                        "total": str(estimate.total_usd),
                    },
                    "within_budget": estimate.total_usd <= budget.limit_usd,
                }
            )
        )
        return 0 if estimate.total_usd <= budget.limit_usd else 1
    if args.command == "prepare-audio":
        command = build_audio_extraction_command(args.input_media, args.output_audio)
        if args.dry_run:
            print(json.dumps({"command": command}))
            return 0
        prepare_audio(args.input_media, args.output_audio)
        return 0

    pipeline = SubtitlePipeline(
        MockTranscriptProvider(_JAPANESE_ASS),
        MockTranslationProvider(_KOREAN_ASS),
    )
    result = pipeline.run("mock://authorized-sample", BudgetLedger(args.budget_usd))
    print(
        json.dumps(
            {
                "stage": result.stage.value,
                "stage_history": [stage.value for stage in result.stage_history],
                "actual_cost_usd": result.actual_cost_usd,
                "failure_reason": result.failure_reason,
                "korean_ass": result.korean_ass,
            },
            ensure_ascii=False,
        )
    )
    return 0 if result.stage.value == "completed" else 1
