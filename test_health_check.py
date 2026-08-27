import health_check


def test_health_summary_reports_missing_required_password(monkeypatch):
    monkeypatch.delenv("NEXUS_PASSWORD", raising=False)
    monkeypatch.setattr(health_check, "_has_secret", lambda name: False)
    monkeypatch.setattr(health_check.shutil, "which", lambda name: "/usr/bin/ffmpeg" if name == "ffmpeg" else None)
    result = health_check.summary()
    assert result["ok"] is False
    assert "NEXUS_PASSWORD" in result["required_failed"]


def test_health_summary_accepts_ready_runtime(monkeypatch):
    monkeypatch.setattr(health_check.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(health_check.shutil, "which", lambda name: "/usr/bin/ffmpeg")
    monkeypatch.setattr(health_check, "_has_secret", lambda name: True)
    result = health_check.summary()
    assert result["ok"] is True
    assert result["ready_for_media"] is True
