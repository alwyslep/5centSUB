import json

from fivecentsub.cli import main


def test_demo_is_offline_and_reports_completed_job(capsys) -> None:
    assert main(["demo"]) == 0

    result = json.loads(capsys.readouterr().out)

    assert result["stage"] == "completed"
    assert result["stage_history"] == ["created", "transcribing", "translating", "completed"]
    assert result["actual_cost_usd"] == "0.017000"


def test_validate_srt_reports_cue_count(tmp_path, capsys) -> None:
    path = tmp_path / "valid.srt"
    path.write_text("1\n00:00:00,000 --> 00:00:01,000\n테스트\n", encoding="utf-8")

    assert main(["validate-srt", str(path)]) == 0

    assert json.loads(capsys.readouterr().out) == {"valid": True, "cues": 1}


def test_estimate_reports_when_a_job_exceeds_budget(capsys) -> None:
    assert (
        main(
            [
                "estimate",
                "--source-seconds",
                "14400",
                "--speech-seconds",
                "7200",
                "--audio-tokens-per-second",
                "25",
                "--asr-input-usd-per-million",
                "0.15",
                "--asr-output-tokens",
                "42000",
                "--asr-output-usd-per-million",
                "1.25",
                "--translation-input-tokens",
                "42000",
                "--translation-input-usd-per-million",
                "0.15",
                "--translation-output-tokens",
                "42000",
                "--translation-output-usd-per-million",
                "1.25",
            ]
        )
        == 1
    )

    assert json.loads(capsys.readouterr().out)["within_budget"] is False


def test_prepare_audio_dry_run_does_not_invoke_ffmpeg(capsys) -> None:
    assert main(["prepare-audio", "input.mp4", "output.flac", "--dry-run"]) == 0

    assert json.loads(capsys.readouterr().out)["command"][0] == "ffmpeg"
