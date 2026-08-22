from __future__ import annotations

from pathlib import Path

from PIL import Image


def test_render_project_smoke(tmp_path, monkeypatch):
    monkeypatch.setattr("video_machine.project_store.PROJECT_ROOT", tmp_path / "projects")
    from video_machine.project_store import add_scene, create_project, save_project
    from video_machine.render_engine import render_project

    source = tmp_path / "source.jpg"
    Image.new("RGB", (720, 720), "#22D3EE").save(source)
    project = create_project("Produto de teste", target_duration_seconds=2)
    project.source_image_path = str(source)
    add_scene(project, label="Hook", text="Teste de render", duration_seconds=1, caption="Teste de render")
    add_scene(project, label="CTA", text="Ver detalhes", duration_seconds=1, caption="Ver detalhes")
    save_project(project)

    result = render_project(project, output_dir=tmp_path / "output")

    assert Path(result["render_path"]).is_file()
    assert Path(result["thumbnail_path"]).is_file()
    assert Path(result["subtitle_path"]).is_file()
    assert Path(result["render_path"]).stat().st_size > 1000
