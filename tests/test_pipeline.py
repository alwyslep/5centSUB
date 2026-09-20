from decimal import Decimal

from fivecentsub.budget import BudgetLedger
from fivecentsub.pipeline import JobStage, SubtitlePipeline
from fivecentsub.providers import MockTranscriptProvider, MockTranslationProvider
from fivecentsub.ass import parse_ass


HEADER = """[Script Info]
Title: test
ScriptType: v4.00+

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

JAPANESE_ASS = (
    HEADER + "Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,はい。\n"
)

KOREAN_ASS = (
    HEADER + "Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,네.\n"
)


def test_mock_pipeline_produces_valid_korean_ass() -> None:
    pipeline = SubtitlePipeline(
        MockTranscriptProvider(JAPANESE_ASS, actual_cost_usd=Decimal("0.01")),
        MockTranslationProvider(KOREAN_ASS, actual_cost_usd=Decimal("0.01")),
    )

    result = pipeline.run("mock://sample", BudgetLedger("0.05"))

    assert result.stage is JobStage.COMPLETED
    assert result.stage_history == (
        JobStage.CREATED,
        JobStage.TRANSCRIBING,
        JobStage.TRANSLATING,
        JobStage.COMPLETED,
    )
    assert result.actual_cost_usd == "0.020000"
    assert [cue.text for cue in parse_ass(result.korean_ass or "")] == ["네."]


def test_pipeline_stops_before_calling_providers_when_estimate_exceeds_budget() -> None:
    pipeline = SubtitlePipeline(
        MockTranscriptProvider(JAPANESE_ASS, estimate_usd=Decimal("0.04")),
        MockTranslationProvider(KOREAN_ASS, estimate_usd=Decimal("0.02")),
    )

    result = pipeline.run("mock://sample", BudgetLedger("0.05"))

    assert result.stage is JobStage.FAILED
    assert result.stage_history == (JobStage.CREATED, JobStage.FAILED)
    assert result.actual_cost_usd == "0.000000"
    assert "Projected cost" in (result.failure_reason or "")


def test_pipeline_reports_actual_charge_over_budget() -> None:
    pipeline = SubtitlePipeline(
        MockTranscriptProvider(JAPANESE_ASS, actual_cost_usd=Decimal("0.04")),
        MockTranslationProvider(KOREAN_ASS, actual_cost_usd=Decimal("0.02")),
    )

    result = pipeline.run("mock://sample", BudgetLedger("0.05"))

    assert result.stage is JobStage.FAILED
    assert result.stage_history == (
        JobStage.CREATED,
        JobStage.TRANSCRIBING,
        JobStage.TRANSLATING,
        JobStage.FAILED,
    )
    assert result.actual_cost_usd == "0.060000"
    assert "Actual cost" in (result.failure_reason or "")
