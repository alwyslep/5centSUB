"""Offline-first job coordinator for future cloud subtitle providers."""

from dataclasses import dataclass
from enum import Enum

from .budget import BudgetExceededError, BudgetLedger
from .providers import TranscriptProvider, TranslationProvider
from .srt import parse_srt


class JobStage(str, Enum):
    CREATED = "created"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class JobResult:
    stage: JobStage
    stage_history: tuple[JobStage, ...]
    korean_srt: str | None
    actual_cost_usd: str
    failure_reason: str | None = None


class SubtitlePipeline:
    def __init__(self, transcript_provider: TranscriptProvider, translation_provider: TranslationProvider):
        self.transcript_provider = transcript_provider
        self.translation_provider = translation_provider

    def run(self, media_reference: str, ledger: BudgetLedger) -> JobResult:
        stage_history = [JobStage.CREATED]
        try:
            ledger.authorize(self.transcript_provider.estimate_usd)
            ledger.authorize(self.translation_provider.estimate_usd)

            stage_history.append(JobStage.TRANSCRIBING)
            transcript = self.transcript_provider.transcribe(media_reference)
            parse_srt(transcript.subtitle_srt)
            ledger.record_charge(transcript.actual_cost_usd)

            stage_history.append(JobStage.TRANSLATING)
            translation = self.translation_provider.translate(transcript.subtitle_srt)
            parse_srt(translation.subtitle_srt)
            ledger.record_charge(translation.actual_cost_usd)
        except (BudgetExceededError, ValueError) as exc:
            stage_history.append(JobStage.FAILED)
            return JobResult(
                JobStage.FAILED,
                tuple(stage_history),
                None,
                f"{ledger.actual_usd:.6f}",
                str(exc),
            )
        stage_history.append(JobStage.COMPLETED)
        return JobResult(
            JobStage.COMPLETED,
            tuple(stage_history),
            translation.subtitle_srt,
            f"{ledger.actual_usd:.6f}",
        )
