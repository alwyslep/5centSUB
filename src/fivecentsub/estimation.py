"""Provider-neutral cost estimation from measured usage."""

from dataclasses import dataclass
from decimal import Decimal

from .budget import as_usd


_MILLION = Decimal("1000000")


def _non_negative(value: Decimal | str | int | float, name: str) -> Decimal:
    amount = as_usd(value)
    if amount < 0:
        raise ValueError(f"{name} cannot be negative")
    return amount


@dataclass(frozen=True)
class UsageEstimate:
    source_seconds: Decimal
    speech_seconds: Decimal
    audio_tokens_per_second: Decimal
    asr_output_tokens: Decimal
    translation_input_tokens: Decimal
    translation_output_tokens: Decimal

    def __post_init__(self) -> None:
        for name in (
            "source_seconds",
            "speech_seconds",
            "audio_tokens_per_second",
            "asr_output_tokens",
            "translation_input_tokens",
            "translation_output_tokens",
        ):
            object.__setattr__(self, name, _non_negative(getattr(self, name), name))
        if self.speech_seconds > self.source_seconds:
            raise ValueError("speech_seconds cannot exceed source_seconds")

    @property
    def asr_input_tokens(self) -> Decimal:
        return self.speech_seconds * self.audio_tokens_per_second

    @property
    def speech_ratio(self) -> Decimal:
        if not self.source_seconds:
            return Decimal("0")
        return self.speech_seconds / self.source_seconds


@dataclass(frozen=True)
class RateCard:
    asr_input_usd_per_million: Decimal
    asr_output_usd_per_million: Decimal
    translation_input_usd_per_million: Decimal
    translation_output_usd_per_million: Decimal

    def __post_init__(self) -> None:
        for name in (
            "asr_input_usd_per_million",
            "asr_output_usd_per_million",
            "translation_input_usd_per_million",
            "translation_output_usd_per_million",
        ):
            object.__setattr__(self, name, _non_negative(getattr(self, name), name))


@dataclass(frozen=True)
class CostEstimate:
    asr_input_usd: Decimal
    asr_output_usd: Decimal
    translation_input_usd: Decimal
    translation_output_usd: Decimal

    @property
    def total_usd(self) -> Decimal:
        return (
            self.asr_input_usd
            + self.asr_output_usd
            + self.translation_input_usd
            + self.translation_output_usd
        ).quantize(Decimal("0.000001"))


def estimate_cost(usage: UsageEstimate, rates: RateCard) -> CostEstimate:
    return CostEstimate(
        asr_input_usd=(usage.asr_input_tokens / _MILLION * rates.asr_input_usd_per_million).quantize(
            Decimal("0.000001")
        ),
        asr_output_usd=(usage.asr_output_tokens / _MILLION * rates.asr_output_usd_per_million).quantize(
            Decimal("0.000001")
        ),
        translation_input_usd=(
            usage.translation_input_tokens / _MILLION * rates.translation_input_usd_per_million
        ).quantize(Decimal("0.000001")),
        translation_output_usd=(
            usage.translation_output_tokens / _MILLION * rates.translation_output_usd_per_million
        ).quantize(Decimal("0.000001")),
    )
