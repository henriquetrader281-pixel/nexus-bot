"""Validações determinísticas antes de exportar ou publicar manualmente."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .project_store import VideoProject, platform_duration_limit


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "severity": self.severity, "message": self.message}


def validate_project(project: VideoProject) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    active = [scene for scene in project.scenes if scene.enabled]
    if not active:
        issues.append(ValidationIssue("no_scenes", "blocking", "Adicione ao menos uma cena ativa."))
    if project.aspect_ratio != "9:16":
        issues.append(ValidationIssue("aspect_ratio", "blocking", "O preset do MVP deve ser vertical 9:16."))
    if project.width != 1080 or project.height != 1920:
        issues.append(ValidationIssue("canvas", "warning", "O canvas atual não é 1080x1920; confirme a compatibilidade do canal."))
    if project.total_duration_seconds > platform_duration_limit(project.platform):
        issues.append(ValidationIssue("duration", "blocking", f"A duração ativa excede o limite aplicado a {project.platform}."))
    if not project.disclosure.strip():
        issues.append(ValidationIssue("disclosure", "warning", "Inclua uma indicação de conteúdo promocional quando houver intenção comercial."))
    for scene in active:
        if not scene.text.strip():
            issues.append(ValidationIssue("empty_scene", "blocking", f"A cena {scene.scene_id} não possui texto principal."))
        if not scene.caption.strip():
            issues.append(ValidationIssue("missing_caption", "warning", f"A cena {scene.scene_id} não possui legenda."))
        if scene.duration_seconds < 0.5:
            issues.append(ValidationIssue("short_scene", "warning", f"A cena {scene.scene_id} é muito curta para leitura."))
    if project.compliance.get("blocking_issues"):
        issues.append(ValidationIssue("compliance", "blocking", "A checklist de conformidade retornou impedimentos."))
    return issues


def validation_summary(project: VideoProject) -> dict[str, Any]:
    issues = validate_project(project)
    blocking = [issue.to_dict() for issue in issues if issue.severity == "blocking"]
    warnings = [issue.to_dict() for issue in issues if issue.severity == "warning"]
    return {
        "ok": not blocking,
        "blocking": blocking,
        "warnings": warnings,
        "review_required": True,
        "publication": "manual_only",
    }


__all__ = ["ValidationIssue", "validate_project", "validation_summary"]
