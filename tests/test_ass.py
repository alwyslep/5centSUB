import pytest

from fivecentsub.ass import parse_ass


HEADER = """[Script Info]
Title: test
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000019FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def test_parse_ass_reads_dialogue_timeline() -> None:
    source = (
        HEADER
        + "Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,はい。\n"
        + "Dialogue: 0,0:00:01.00,0:00:02.50,Default,,0,0,0,,{\\i1}いいえ{\\i0}。\n"
    )

    cues = parse_ass(source)

    assert [(cue.number, cue.start_ms, cue.end_ms, cue.text) for cue in cues] == [
        (1, 0, 1000, "はい。"),
        (2, 1000, 2500, "いいえ。"),
    ]


def test_parse_ass_rejects_overlapping_dialogues() -> None:
    source = (
        HEADER
        + "Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,첫 번째\n"
        + "Dialogue: 0,0:00:01.99,0:00:03.00,Default,,0,0,0,,두 번째\n"
    )

    with pytest.raises(ValueError, match="overlaps"):
        parse_ass(source)


def test_parse_ass_rejects_invalid_timestamp() -> None:
    source = (
        HEADER
        + "Dialogue: 0,00:00:00,000,0:00:01.00,Default,,0,0,0,,SRT식 시간\n"
    )

    with pytest.raises(ValueError, match="invalid timestamp"):
        parse_ass(source)


def test_parse_ass_rejects_missing_events_section() -> None:
    with pytest.raises(ValueError, match="no \\[Events\\] section"):
        parse_ass("[Script Info]\nTitle: test\n")


def test_parse_ass_rejects_non_positive_duration() -> None:
    source = (
        HEADER
        + "Dialogue: 0,0:00:02.00,0:00:02.00,Default,,0,0,0,,길이 없음\n"
    )

    with pytest.raises(ValueError, match="non-positive duration"):
        parse_ass(source)
