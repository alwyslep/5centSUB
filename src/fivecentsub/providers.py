"""Provider contracts and deterministic offline providers."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class ProviderResponse:
    subtitle_srt: str
    actual_cost_usd: Decimal


class TranscriptProvider(Protocol):
    estimate_usd: Decimal

    def transcribe(self, media_reference: str) -> ProviderResponse:
        """Return a Japanese SRT transcript for the supplied media reference."""


class TranslationProvider(Protocol):
    estimate_usd: Decimal

    def translate(self, japanese_srt: str) -> ProviderResponse:
        """Return a Korean SRT translation that preserves the cue timeline."""


@dataclass(frozen=True)
class MockTranscriptProvider:
    subtitle_srt: str
    estimate_usd: Decimal = Decimal("0.010000")
    actual_cost_usd: Decimal = Decimal("0.009000")

    def transcribe(self, media_reference: str) -> ProviderResponse:
        return ProviderResponse(self.subtitle_srt, self.actual_cost_usd)


@dataclass(frozen=True)
class MockTranslationProvider:
    subtitle_srt: str
    estimate_usd: Decimal = Decimal("0.010000")
    actual_cost_usd: Decimal = Decimal("0.008000")

    def translate(self, japanese_srt: str) -> ProviderResponse:
        return ProviderResponse(self.subtitle_srt, self.actual_cost_usd)
