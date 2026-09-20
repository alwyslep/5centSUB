from decimal import Decimal

import pytest

from fivecentsub.estimation import RateCard, UsageEstimate, estimate_cost


def test_estimate_cost_includes_all_billable_components() -> None:
    usage = UsageEstimate(
        source_seconds=Decimal("14400"),
        speech_seconds=Decimal("7200"),
        audio_tokens_per_second=Decimal("25"),
        asr_output_tokens=Decimal("42000"),
        translation_input_tokens=Decimal("42000"),
        translation_output_tokens=Decimal("42000"),
    )
    rates = RateCard(
        asr_input_usd_per_million=Decimal("0.15"),
        asr_output_usd_per_million=Decimal("1.25"),
        translation_input_usd_per_million=Decimal("0.15"),
        translation_output_usd_per_million=Decimal("1.25"),
    )

    estimate = estimate_cost(usage, rates)

    assert usage.speech_ratio == Decimal("0.5")
    assert estimate.asr_input_usd == Decimal("0.027000")
    assert estimate.total_usd == Decimal("0.138300")


def test_usage_rejects_speech_longer_than_source() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        UsageEstimate("60", "61", "25", "1", "1", "1")
