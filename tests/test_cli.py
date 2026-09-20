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
