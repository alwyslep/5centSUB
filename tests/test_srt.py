import pytest

from fivecentsub.srt import parse_srt


def test_parse_srt_rejects_overlapping_cues() -> None:
    source = """1
00:00:00,000 --> 00:00:02,000
첫 번째

2
00:00:01,999 --> 00:00:03,000
두 번째
"""

    with pytest.raises(ValueError, match="overlaps"):
        parse_srt(source)


def test_parse_srt_requires_sequential_numbers() -> None:
    source = """2
00:00:00,000 --> 00:00:01,000
잘못된 번호
"""

    with pytest.raises(ValueError, match="Cue number must be 1"):
        parse_srt(source)
