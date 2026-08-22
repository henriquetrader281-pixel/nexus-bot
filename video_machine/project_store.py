"""Persistência leve e versionada dos projetos da Máquina de Vídeos."""

from __future__ import annotations

import json
import re
import uuid
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR / ".nexus_media" / "video_projects"
SCHEMA_VERSION = 1
MAX_PROJECT_DURATION_SECONDS = 900
YOUTUBE_SHORTS_MAX_SECONDS = 180


def platform_duration_limit(platform: str) -> int:
    normalized = str(platform or "").lower()
    if "youtube" in normalized and "short" in normalized:
        return YOUTUBE_SHORTS_MAX_SECONDS
    return MAX_PROJECT_DURATION_SECONDS


@dataclass
class Scene:
    scene_id: str
    label: str
    text: str
    duration_seconds: float = 3.0
    media_path: str | None = None
    media_url: str | None = None
    visual_prompt: str = ""
    caption: str = ""
    transition: str = "hard_cut"
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VideoProject:
    project_id: str
    title: str
    product_name: str
    niche: str = ""
    platform: str = "TikTok"
    aspect_ratio: str = "9:16"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    duration_limit_seconds: int = 900
    target_duration_seconds: int = 24
    tone: str = "direto e demonstrativo"
    goal: str = "apresentar uma solução com clareza"
    scenes: list[Scene] = field(default_factory=list)
    audio_path: str | None = None
    subtitle_path: str | None = None
    thumbnail_path: str | None = None
    render_path: str | None = None
    source_image_path: str | None = None
    source_image_url: str | None = None
    disclosure: str = "Conteúdo promocional: verifique detalhes antes de comprar."
    status: str = "draft"
    version: int = 1
    created_at: str = ""
    updated_at: str = ""
    agent_runs: list[dict[str, Any]] = field(default_factory=list)
    memory_tags: list[str] = field(default_factory=list)
    compliance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.created_at = self.created_at or now
        self.updated_at = self.updated_at or now
        self.duration_limit_seconds = min(max(1, int(self.duration_limit_seconds)), platform_duration_limit(self.platform))
        self.target_duration_seconds = max(1, min(int(self.target_duration_seconds), self.duration_limit_seconds))
        self.scenes = [scene if isinstance(scene, Scene) else Scene(**scene) for scene in self.scenes]

    @property
    def total_duration_seconds(self) -> float:
        return round(sum(scene.duration_seconds for scene in self.scenes if scene.enabled), 2)

    def touch(self) -> None:
        self.version += 1
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = SCHEMA_VERSION
        data["total_duration_seconds"] = self.total_duration_seconds
        return data


def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9À-ÿ]+", "_", str(value or "projeto")).strip("_")
    return value[:60] or "projeto"


def _project_path(project_id: str) -> Path:
    return PROJECT_ROOT / f"{_slug(project_id)}.json"


def create_project(product_name: str, *, title: str | None = None, niche: str = "", platform: str = "TikTok", target_duration_seconds: int = 24) -> VideoProject:
    product_name = str(product_name or "Projeto sem nome").strip()
    return VideoProject(
        project_id=f"video-{uuid.uuid4().hex[:10]}",
        title=title or f"Projeto: {product_name}",
        product_name=product_name,
        niche=niche,
        platform=platform,
        target_duration_seconds=target_duration_seconds,
    )


def project_from_dict(data: dict[str, Any]) -> VideoProject:
    payload = deepcopy(data)
    payload.pop("schema_version", None)
    payload.pop("total_duration_seconds", None)
    payload["scenes"] = [scene if isinstance(scene, Scene) else Scene(**scene) for scene in payload.get("scenes", [])]
    allowed = set(VideoProject.__dataclass_fields__.keys())
    return VideoProject(**{key: value for key, value in payload.items() if key in allowed})


def save_project(project: VideoProject) -> Path:
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    project.touch()
    path = _project_path(project.project_id)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(project.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)
    return path


def load_project(project_id: str) -> VideoProject:
    path = _project_path(project_id)
    if not path.is_file():
        raise FileNotFoundError(f"Projeto não encontrado: {project_id}")
    return project_from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_projects() -> list[VideoProject]:
    if not PROJECT_ROOT.exists():
        return []
    projects: list[VideoProject] = []
    for path in sorted(PROJECT_ROOT.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            projects.append(project_from_dict(json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, ValueError, TypeError, KeyError):
            continue
    return projects


def add_scene(project: VideoProject, *, label: str, text: str, duration_seconds: float = 3.0, visual_prompt: str = "", caption: str = "", media_path: str | None = None, media_url: str | None = None, transition: str = "hard_cut") -> Scene:
    scene = Scene(
        scene_id=f"scene-{uuid.uuid4().hex[:8]}",
        label=str(label or "Cena").strip(),
        text=str(text or "").strip(),
        duration_seconds=max(0.5, min(float(duration_seconds), 120.0)),
        visual_prompt=str(visual_prompt or "").strip(),
        caption=str(caption or text or "").strip(),
        media_path=media_path,
        media_url=media_url,
        transition=transition if transition in {"hard_cut", "fade_short"} else "hard_cut",
    )
    project.scenes.append(scene)
    project.touch()
    return scene


def update_scene(project: VideoProject, scene_id: str, **updates: Any) -> Scene:
    for scene in project.scenes:
        if scene.scene_id == scene_id:
            for key, value in updates.items():
                if key in {"label", "text", "visual_prompt", "caption", "media_path", "media_url", "transition"} and value is not None:
                    setattr(scene, key, str(value))
                elif key == "duration_seconds" and value is not None:
                    scene.duration_seconds = max(0.5, min(float(value), 120.0))
                elif key == "enabled" and value is not None:
                    scene.enabled = bool(value)
            project.touch()
            return scene
    raise KeyError(f"Cena não encontrada: {scene_id}")


def remove_scene(project: VideoProject, scene_id: str) -> None:
    before = len(project.scenes)
    project.scenes = [scene for scene in project.scenes if scene.scene_id != scene_id]
    if len(project.scenes) == before:
        raise KeyError(f"Cena não encontrada: {scene_id}")
    project.touch()


def ensure_scene_duration(project: VideoProject) -> None:
    """Distribui a duração alvo pelas cenas sem ultrapassar 15 minutos."""
    enabled = [scene for scene in project.scenes if scene.enabled]
    if not enabled:
        return
    target = min(max(float(project.target_duration_seconds), 1.0), float(project.duration_limit_seconds))
    each = max(0.5, round(target / len(enabled), 2))
    for scene in enabled:
        scene.duration_seconds = each
    project.touch()


__all__ = ["MAX_PROJECT_DURATION_SECONDS", "PROJECT_ROOT", "SCHEMA_VERSION", "Scene", "VideoProject", "YOUTUBE_SHORTS_MAX_SECONDS", "add_scene", "create_project", "ensure_scene_duration", "list_projects", "load_project", "platform_duration_limit", "remove_scene", "save_project", "update_scene"]
