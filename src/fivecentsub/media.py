"""Local non-ML media preparation."""

from pathlib import Path
import subprocess
from typing import Callable, Sequence


def build_audio_extraction_command(input_media: Path, output_audio: Path) -> tuple[str, ...]:
    """Build the canonical FFmpeg command for 16 kHz mono FLAC extraction."""
    if output_audio.suffix.lower() != ".flac":
        raise ValueError("Output audio must use the .flac extension")
    return (
        "ffmpeg",
        "-nostdin",
        "-y",
        "-i",
        str(input_media),
        "-vn",
        "-map",
        "0:a:0",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "flac",
        str(output_audio),
    )


def prepare_audio(
    input_media: Path,
    output_audio: Path,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> None:
    """Extract audio locally without performing ML inference."""
    runner(build_audio_extraction_command(input_media, output_audio), check=True)
