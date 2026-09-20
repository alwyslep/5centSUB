"""Strict parsing for the SRT contract used by the pipeline."""

from dataclasses import dataclass
import re


_TIMECODE = re.compile(
    r"^(?P<start_hour>\d{2,}):(?P<start_minute>[0-5]\d):(?P<start_second>[0-5]\d),(?P<start_ms>\d{3})"
    r" --> "
    r"(?P<end_hour>\d{2,}):(?P<end_minute>[0-5]\d):(?P<end_second>[0-5]\d),(?P<end_ms>\d{3})$"
)


@dataclass(frozen=True)
class Cue:
    number: int
    start_ms: int
    end_ms: int
    text: str


def _milliseconds(match: re.Match[str], prefix: str) -> int:
    return (
        ((int(match[f"{prefix}_hour"]) * 60 + int(match[f"{prefix}_minute"])) * 60
        + int(match[f"{prefix}_second"]))
        * 1000
        + int(match[f"{prefix}_ms"])
    )


def parse_srt(source: str) -> list[Cue]:
    normalized = source.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not normalized:
        raise ValueError("SRT is empty")

    cues: list[Cue] = []
    for expected_number, block in enumerate(normalized.split("\n\n"), start=1):
        lines = block.split("\n")
        if len(lines) < 3:
            raise ValueError(f"Cue {expected_number} is incomplete")
        if not lines[0].isdigit() or int(lines[0]) != expected_number:
            raise ValueError(f"Cue number must be {expected_number}")
        match = _TIMECODE.fullmatch(lines[1])
        if not match:
            raise ValueError(f"Cue {expected_number} has an invalid timestamp")

        text = "\n".join(lines[2:]).strip()
        if not text:
            raise ValueError(f"Cue {expected_number} has no text")
        start_ms = _milliseconds(match, "start")
        end_ms = _milliseconds(match, "end")
        if end_ms <= start_ms:
            raise ValueError(f"Cue {expected_number} has a non-positive duration")
        if cues and start_ms < cues[-1].end_ms:
            raise ValueError(f"Cue {expected_number} overlaps cue {cues[-1].number}")
        cues.append(Cue(expected_number, start_ms, end_ms, text))
    return cues
