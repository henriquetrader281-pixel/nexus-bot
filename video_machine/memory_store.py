"""Memória local da Máquina de Vídeos.

A memória guarda decisões e resultados observáveis, não inventa desempenho. O
histórico é limitado para evitar crescimento indefinido do arquivo e cada item
mantém a origem para auditoria.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_PATH = Path(os.getenv("NEXUS_VIDEO_MEMORY", str(BASE_DIR / ".nexus_media" / "video_memory.json")))
MAX_RUNS = 200
MAX_LEARNINGS = 200


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_memory() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "updated_at": _now(),
        "runs": [],
        "learnings": [],
        "preferences": {
            "platform": "TikTok",
            "aspect_ratio": "9:16",
            "max_duration_seconds": 900,
            "default_language": "pt-BR",
        },
        "guardrails": {
            "require_human_review_before_publish": True,
            "allow_unverified_claims": False,
            "allow_automatic_publish": False,
        },
    }


def load_memory() -> dict[str, Any]:
    if not MEMORY_PATH.is_file():
        return default_memory()
    try:
        data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return default_memory()
    if not isinstance(data, dict):
        return default_memory()
    memory = default_memory()
    memory.update({key: value for key, value in data.items() if key in memory})
    for key in ("runs", "learnings"):
        memory[key] = list(memory.get(key) or [])[-(MAX_RUNS if key == "runs" else MAX_LEARNINGS):]
    return memory


def save_memory(memory: dict[str, Any]) -> Path:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(memory)
    payload["updated_at"] = _now()
    payload["runs"] = list(payload.get("runs") or [])[-MAX_RUNS:]
    payload["learnings"] = list(payload.get("learnings") or [])[-MAX_LEARNINGS:]
    temp = MEMORY_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(MEMORY_PATH)
    return MEMORY_PATH


def record_agent_run(*, project_id: str, agent_id: str, provider: str, model: str, output: dict[str, Any], used_fallback: bool, error: str | None = None) -> dict[str, Any]:
    memory = load_memory()
    item = {
        "project_id": project_id,
        "agent_id": agent_id,
        "provider": provider,
        "model": model,
        "output": deepcopy(output),
        "used_fallback": bool(used_fallback),
        "error": error,
        "created_at": _now(),
    }
    memory.setdefault("runs", []).append(item)
    save_memory(memory)
    return item


def record_learning(*, source: str, insight: str, confidence: str = "low", evidence: dict[str, Any] | None = None, tags: list[str] | None = None) -> dict[str, Any]:
    confidence = confidence if confidence in {"low", "medium", "high"} else "low"
    memory = load_memory()
    item = {
        "source": source,
        "insight": str(insight).strip(),
        "confidence": confidence,
        "evidence": deepcopy(evidence or {}),
        "tags": list(tags or []),
        "created_at": _now(),
    }
    memory.setdefault("learnings", []).append(item)
    save_memory(memory)
    return item


def recent_context(*, project_id: str | None = None, agent_id: str | None = None, limit: int = 8) -> dict[str, Any]:
    memory = load_memory()
    runs = list(memory.get("runs") or [])
    learnings = list(memory.get("learnings") or [])
    if project_id:
        runs = [item for item in runs if item.get("project_id") == project_id]
    if agent_id:
        runs = [item for item in runs if item.get("agent_id") == agent_id]
    return {
        "preferences": deepcopy(memory.get("preferences", {})),
        "guardrails": deepcopy(memory.get("guardrails", {})),
        "recent_runs": deepcopy(runs[-max(1, limit):]),
        "recent_learnings": deepcopy(learnings[-max(1, limit):]),
    }


def update_preferences(**updates: Any) -> dict[str, Any]:
    memory = load_memory()
    memory.setdefault("preferences", {}).update({key: value for key, value in updates.items() if value is not None})
    save_memory(memory)
    return deepcopy(memory["preferences"])


def update_guardrails(**updates: Any) -> dict[str, Any]:
    memory = load_memory()
    memory.setdefault("guardrails", {}).update({key: bool(value) for key, value in updates.items() if value is not None})
    save_memory(memory)
    return deepcopy(memory["guardrails"])


__all__ = ["MEMORY_PATH", "default_memory", "load_memory", "record_agent_run", "record_learning", "recent_context", "save_memory", "update_guardrails", "update_preferences"]
