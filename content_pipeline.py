"""Serviço sem interface para gerar uma campanha completa do Nexus.

A camada Streamlit deve apenas recolher entradas e apresentar o resultado. Este
módulo concentra análise, copy, narração, mídia e fila para que o Modo Simples,
a Esteira Principal e futuras automações compartilhem o mesmo contrato.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import campaign_queue
import campaign_state
from media_pipeline import generate_campaign_media
from simple_mode import analisar_palavras_chave, gerar_copy


@dataclass
class PipelineResult:
    campaign: dict[str, Any]
    status: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    manifest: dict[str, Any] | None = None
    queue_id: int | None = None

    @property
    def ready(self) -> bool:
        return self.status == "ready"


def _failure(campaign: dict[str, Any], message: str) -> PipelineResult:
    return PipelineResult(dict(campaign), "blocked", errors=[message])


def _analysis(campaign: dict[str, Any]) -> dict[str, Any]:
    return analisar_palavras_chave(
        campaign["product_name"],
        campaign.get("pain", "Necessidade identificada no mercado"),
        ", ".join(campaign.get("keywords", []) or []),
        campaign.get("trends"),
    )


def generate_campaign_package(
    campaign: dict[str, Any] | None = None,
    *,
    output_root: str | Path = ".nexus_media",
    save_queue: bool = True,
) -> PipelineResult:
    """Gera o pacote completo sem depender do Streamlit.

    Falhas de áudio são não bloqueantes; falhas de mídia são reportadas como
    ``needs_review``. A fila só é atualizada quando ``save_queue`` é verdadeiro.
    """
    current = dict(campaign or campaign_state.get_campaign() or {})
    product = str(current.get("product_name") or "").strip()
    if not product:
        return _failure(current, "Nenhum produto foi selecionado para a campanha.")

    warnings: list[str] = []
    errors: list[str] = []
    try:
        analysis = _analysis(current)
    except Exception as exc:
        return _failure(current, f"Não foi possível analisar a campanha: {exc}")

    try:
        copy_text, copy_warning = gerar_copy(current, analysis)
    except Exception as exc:
        return _failure(current, f"Não foi possível gerar a copy: {exc}")
    if copy_warning:
        warnings.append(str(copy_warning))

    updated = campaign_state.set_campaign(
        **current,
        copy=copy_text,
        copy_final=copy_text,
        hooks=analysis["hooks"],
        keywords=analysis["keywords"],
        caption=analysis["caption"],
        cta_variations=analysis["cta_variations"],
        intent=analysis["intent"],
        intent_label=analysis["intent_label"],
    )
    current = dict(updated or current)

    try:
        import tts_engine

        voice = tts_engine.gerar_narração_ia(copy_text)
    except Exception as exc:
        voice = {"success": False, "error": str(exc)}
    if voice.get("success") and voice.get("audio_path"):
        current = dict(campaign_state.set_campaign(audio_path=voice["audio_path"]) or current)
        if voice.get("aviso"):
            warnings.append(str(voice["aviso"]))
    else:
        warnings.append(f"Áudio indisponível: {voice.get('error', 'provedor não configurado')}")

    manifest: dict[str, Any] | None = None
    try:
        current = dict(campaign_state.get_campaign() or current)
        manifest = generate_campaign_media(current, output_root=output_root)
        current = dict(campaign_state.set_campaign(
            source_image_path=manifest.get("source_image_path"),
            image_path=manifest.get("image_a"),
            video_path=manifest.get("video_b"),
            image_url=manifest.get("product", {}).get("image_url") or current.get("image_url"),
            media_manifest=manifest,
        ) or current)
    except Exception as exc:
        errors.append(f"Mídia não gerada: {exc}")

    status = "ready" if manifest is not None and not errors else "needs_review"
    queue_id: int | None = None
    if save_queue and status != "blocked":
        queue_id = campaign_queue.save_prepared_campaign(current, status=status)
        current = dict(campaign_state.set_campaign(
            queue_id=queue_id,
            queue_status=status,
            publication_status="manual_only",
        ) or current)

    return PipelineResult(current, status, warnings, errors, manifest, queue_id)


__all__ = ["PipelineResult", "generate_campaign_package"]
