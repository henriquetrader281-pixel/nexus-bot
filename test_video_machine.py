from __future__ import annotations

import json


def test_local_agents_return_contracts(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_VIDEO_MEMORY", str(tmp_path / "memory.json"))
    from video_machine.agents import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    context = {"product_name": "Garrafa térmica", "niche": "trilhas", "platform": "TikTok", "target_duration_seconds": 24}
    script = orchestrator.run("roteiro", context)
    visual = orchestrator.run("direcao_visual", context)

    assert script.used_fallback is True
    assert script.output["scenes"]
    assert visual.output["visual_identity"]["palette"]


def test_project_round_trip_and_duration(tmp_path, monkeypatch):
    monkeypatch.setattr("video_machine.project_store.PROJECT_ROOT", tmp_path / "projects")
    from video_machine.project_store import add_scene, create_project, ensure_scene_duration, load_project, save_project

    project = create_project("Organizador de cozinha", target_duration_seconds=18)
    add_scene(project, label="Hook", text="Veja esta gaveta", duration_seconds=2)
    add_scene(project, label="Demonstração", text="Organize em segundos", duration_seconds=8)
    ensure_scene_duration(project)
    path = save_project(project)
    loaded = load_project(project.project_id)

    assert path.is_file()
    assert loaded.total_duration_seconds == 18.0
    assert loaded.scenes[0].scene_id == project.scenes[0].scene_id
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1

    shorts = create_project("Tema Shorts", platform="YouTube Shorts", target_duration_seconds=900)
    assert shorts.duration_limit_seconds == 180
    assert shorts.target_duration_seconds == 180


def test_memory_records_are_bounded_and_auditable(tmp_path, monkeypatch):
    monkeypatch.setattr("video_machine.memory_store.MEMORY_PATH", tmp_path / "memory.json")
    from video_machine.memory_store import load_memory, record_agent_run, record_learning, recent_context

    record_agent_run(project_id="video-1", agent_id="roteiro", provider="local", model="local", output={"ok": True}, used_fallback=True)
    record_learning(source="test", insight="Hook demonstrativo", confidence="medium", evidence={"impressions": 10}, tags=["hook"])
    context = recent_context(project_id="video-1")

    assert context["recent_runs"][0]["agent_id"] == "roteiro"
    assert context["recent_learnings"][0]["confidence"] == "medium"
    assert load_memory()["guardrails"]["require_human_review_before_publish"] is True
