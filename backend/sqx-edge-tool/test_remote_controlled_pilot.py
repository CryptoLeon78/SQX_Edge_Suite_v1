import json
import os

from core.remote_access import evaluate_remote_session
from core.remote_pilot import REMOTE_CONTROLLED_PILOT_VERSION, run_controlled_pilot_drill


def test_remote8_controlled_pilot_drill_proves_end_to_end_without_public_paths(tmp_path):
    result = run_controlled_pilot_drill(base_dir=tmp_path, run_id="remote8-test")

    assert result["ok"] is True
    assert result["version"] == REMOTE_CONTROLLED_PILOT_VERSION
    assert result["phases"]["paymentWebhook"]["ok"] is True
    assert result["phases"]["login"]["ok"] is True
    assert result["phases"]["workspace"]["ok"] is True
    assert result["phases"]["artifactGeneration"]["filename"].endswith(".cfx")
    assert result["phases"]["exportDownload"]["sha256Matches"] is True
    assert result["phases"]["isolation"]["ok"] is True
    assert result["phases"]["isolation"]["sameWorkspace"] is False
    assert result["phases"]["isolation"]["firstArtifactVisibleInSecondWorkspace"] is False
    assert result["phases"]["revocation"]["accessAllowedAfterCancel"] is False
    assert result["phases"]["restore"]["accessAllowedAfterRestore"] is True
    assert result["privacy"]["rawEmailReturned"] is False
    assert result["privacy"]["sessionTokenReturned"] is False
    assert result["privacy"]["localPathsReturned"] is False
    assert result["expansionGate"]["allowedToExpandBeyondOneUser"] is False

    serialized = json.dumps(result)
    assert "remote8-buyer@example.invalid" not in serialized
    assert "remote8-second@example.invalid" not in serialized
    assert str(tmp_path) not in serialized

    summary_path = tmp_path / "remote8-test" / "remote8_controlled_pilot.public.json"
    assert summary_path.is_file()
    assert "remote8-buyer@example.invalid" not in summary_path.read_text(encoding="utf-8")
    assert (tmp_path / "remote8-test" / "remote8_controlled_pilot.local.json").is_file()


def test_remote8_controlled_pilot_restores_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "original-session-secret-0000000000")
    run_controlled_pilot_drill(base_dir=tmp_path, run_id="remote8-env")

    assert evaluate_remote_session("not-a-token")["access"]["reason"] == "session_malformed"
    assert os.environ["SQX_REMOTE_SESSION_SECRET"] == "original-session-secret-0000000000"
