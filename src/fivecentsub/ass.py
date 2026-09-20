"""Strict parsing for the ASS contract used by the pipeline."""

from dataclasses import dataclass
import re


_TIMESTAMP = re.compile(r"^(?P<hour>\d+):(?P<minute>[0-5]\d):(?P<second>[0-5]\d)\.(?P<centisecond>\d{2})$")
_OVERRIDES = re.compile(r"\{[^}]*\}")


@dataclass(frozen=True)
class Cue:
    number: int
    start_ms: int
    end_ms: int
    text: str


def _milliseconds(match: re.Match[str]) -> int:
    return (
        (
            (int(match["hour"]) * 60 + int(match["minute"])) * 60
            + int(match["second"])
        )
        * 100
        + int(match["centisecond"])
    ) * 10


def _clean_text(raw: str) -> str:
    return _OVERRIDES.sub("", raw).replace("\\N", "\n").replace("\\n", "\n").strip()


def parse_ass(source: str) -> list[Cue]:
    normalized = source.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not normalized:
        raise ValueError("ASS is empty")

    in_events = False
    field_names: list[str] | None = None
    dialogue_rows: list[tuple[int, str]] = []
    for lineno, line in enumerate(normalized.split("\n"), start=1):
        stripped = line.strip()
        if stripped.startswith("["):
            in_events = stripped.lower() == "[events]"
            continue
        if not in_events:
            continue
        if stripped.lower().startswith("format:"):
            field_names = [name.strip().lower() for name in stripped[len("format:"):].split(",")]
        elif stripped.lower().startswith("dialogue:"):
            if field_names is None:
                raise ValueError("ASS [Events] has no Format line")
            dialogue_rows.append((lineno, stripped[len("dialogue:"):].lstrip()))

    if field_names is None:
        raise ValueError("ASS has no [Events] section")
    try:
        start_index = field_names.index("start")
        end_index = field_names.index("end")
        text_index = field_names.index("text")
    except ValueError:
        raise ValueError("ASS [Events] Format must include Start, End, and Text") from None

    cues: list[Cue] = []
    for number, (lineno, row) in enumerate(dialogue_rows, start=1):
        parts = row.split(",", len(field_names) - 1)
        if len(parts) != len(field_names):
            raise ValueError(f"Dialogue {number} does not match the Format")
        start_match = _TIMESTAMP.fullmatch(parts[start_index].strip())
        end_match = _TIMESTAMP.fullmatch(parts[end_index].strip())
        if not start_match or not end_match:
            raise ValueError(f"Dialogue {number} has an invalid timestamp")

        text = _clean_text(parts[text_index])
        if not text:
            raise ValueError(f"Dialogue {number} has no text")
        start_ms = _milliseconds(start_match)
        end_ms = _milliseconds(end_match)
        if end_ms <= start_ms:
            raise ValueError(f"Dialogue {number} has a non-positive duration")
        if cues and start_ms < cues[-1].end_ms:
            raise ValueError(f"Dialogue {number} overlaps dialogue {cues[-1].number}")
        cues.append(Cue(number, start_ms, end_ms, text))
    return cues
