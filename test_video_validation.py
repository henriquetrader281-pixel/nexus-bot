from __future__ import annotations


def test_validation_blocks_empty_project():
    from video_machine.project_store import create_project
    from video_machine.validation import validation_summary

    project = create_project("Tema", platform="YouTube Shorts", target_duration_seconds=900)
    summary = validation_summary(project)

    assert summary["ok"] is False
    assert any(item["code"] == "no_scenes" for item in summary["blocking"])
    assert project.duration_limit_seconds == 180


def test_validation_accepts_complete_project(tmp_path, monkeypatch):
    monkeypatch.setattr("video_machine.project_store.PROJECT_ROOT", tmp_path / "projects")
    from video_machine.project_store import add_scene, create_project
    from video_machine.validation import validation_summary

    project = create_project("Tema", target_duration_seconds=6)
    add_scene(project, label="Hook", text="Comece", duration_seconds=3, caption="Comece")
    add_scene(project, label="CTA", text="Confira", duration_seconds=3, caption="Confira")

    summary = validation_summary(project)
    assert summary["ok"] is True
    assert summary["blocking"] == []
