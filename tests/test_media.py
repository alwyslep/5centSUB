from pathlib import Path

import pytest

from fivecentsub.media import build_audio_extraction_command, prepare_audio


def test_build_audio_extraction_command_uses_safe_audio_contract() -> None:
    command = build_audio_extraction_command(Path("input.mp4"), Path("output.flac"))

    assert command == (
        "ffmpeg",
        "-nostdin",
        "-y",
        "-i",
        "input.mp4",
        "-vn",
        "-map",
        "0:a:0",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "flac",
        "output.flac",
    )


def test_prepare_audio_passes_canonical_command_to_runner() -> None:
    calls: list[tuple[tuple[str, ...], bool]] = []

    def runner(command, *, check):
        calls.append((command, check))

    prepare_audio(Path("input.mp4"), Path("output.flac"), runner)

    assert calls == [(build_audio_extraction_command(Path("input.mp4"), Path("output.flac")), True)]


def test_build_audio_extraction_command_requires_flac_output() -> None:
    with pytest.raises(ValueError, match=r"\.flac"):
        build_audio_extraction_command(Path("input.mp4"), Path("output.mp3"))
