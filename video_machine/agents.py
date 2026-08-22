"""Agentes especializados da Máquina de Vídeos Nexus.

O módulo usa um contrato único para permitir trocar o provedor de IA por agente.
Sem credenciais, cada agente cai para uma resposta local determinística e útil;
assim o estúdio continua funcional sem depender de APIs pagas.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


@dataclass(frozen=True)
class AgentSpec:
    """Descrição pública de um agente do estúdio."""

    agent_id: str
    name: str
    specialty: str
    default_model: str
    output_contract: str


@dataclass
class AgentResult:
    """Resultado serializável de uma execução de agente."""

    agent_id: str
    provider: str
    model: str
    output: dict[str, Any]
    used_fallback: bool
    created_at: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


AGENT_SPECS: dict[str, AgentSpec] = {
    "estrategia": AgentSpec(
        "estrategia",
        "Estrategista de audiência",
        "Posicionamento, público e ângulo de retenção",
        "gpt-5-mini",
        "strategy",
    ),
    "roteiro": AgentSpec(
        "roteiro",
        "Roteirista de vídeos curtos",
        "Hook, narrativa por cenas e CTA transparente",
        "gpt-5-mini",
        "script",
    ),
    "direcao_visual": AgentSpec(
        "direcao_visual",
        "Diretor visual",
        "Prompts de imagem, composição e consistência visual",
        "gemini-3-flash-preview",
        "visual",
    ),
    "edicao": AgentSpec(
        "edicao",
        "Editor de ritmo",
        "Timing, cortes, textos na tela e transições",
        "gpt-5-mini",
        "edit_recipe",
    ),
    "voz_legendas": AgentSpec(
        "voz_legendas",
        "Diretor de voz e legendas",
        "Narração, acessibilidade e legibilidade",
        "gpt-5-mini",
        "voice_caption",
    ),
    "thumbnail": AgentSpec(
        "thumbnail",
        "Diretor de capa",
        "Capa vertical, contraste e promessa honesta",
        "gemini-3-flash-preview",
        "thumbnail",
    ),
    "analista": AgentSpec(
        "analista",
        "Analista de métricas",
        "Diagnóstico de retenção e próximos testes",
        "gpt-5-mini",
        "analytics",
    ),
    "conformidade": AgentSpec(
        "conformidade",
        "Revisor de conformidade",
        "Diretrizes de plataforma, publicidade e direitos",
        "gpt-5-mini",
        "compliance",
    ),
}


class AgentProvider(Protocol):
    name: str

    def complete(self, spec: AgentSpec, context: dict[str, Any]) -> dict[str, Any]:
        ...


class LocalProvider:
    """Fallback local sem rede, sem custo por execução e adequado para testes."""

    name = "local"

    def complete(self, spec: AgentSpec, context: dict[str, Any]) -> dict[str, Any]:
        return _local_output(spec, context)


class OpenAICompatibleProvider:
    """Adaptador opcional para endpoints compatíveis com Chat Completions.

    O cliente só é importado quando este provedor é realmente solicitado. Isso
    evita tornar o núcleo dependente de uma chave ou de uma rede disponível.
    """

    name = "openai-compatible"

    def __init__(self, api_key: str, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url

    def complete(self, spec: AgentSpec, context: dict[str, Any]) -> dict[str, Any]:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depende do ambiente
            raise RuntimeError("Instale o pacote openai para usar o provedor remoto.") from exc

        kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        client = OpenAI(**kwargs)
        system = (
            "Você é um agente especializado de uma máquina de vídeos. "
            "Responda somente JSON válido, sem markdown, sem prometer viralização "
            "e sem inventar métricas ou provas. Preserve alegações verificáveis."
        )
        prompt = json.dumps(
            {
                "agente": asdict(spec),
                "contexto": context,
                "contrato": spec.output_contract,
            },
            ensure_ascii=False,
        )
        user_content: Any = prompt
        source_image_url = str(context.get("source_image_url") or "").strip()
        if source_image_url.startswith(("http://", "https://")) and spec.agent_id in {"direcao_visual", "thumbnail"}:
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": source_image_url, "detail": "auto"}},
            ]
        response_kwargs: dict[str, Any] = {
            "model": _model_for(spec),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
        }
        model = response_kwargs["model"]
        if model.startswith("gpt-5"):
            response_kwargs["max_completion_tokens"] = 1800
        else:
            response_kwargs["max_tokens"] = 1800
        response = client.chat.completions.create(**response_kwargs)
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("O agente remoto retornou JSON que não é objeto.")
        return parsed


def _model_for(spec: AgentSpec) -> str:
    key = f"NEXUS_AGENT_{spec.agent_id.upper()}_MODEL"
    return os.getenv(key, spec.default_model)


def _normalise_text(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text or default


def _project_context(context: dict[str, Any]) -> tuple[str, str, str, str]:
    product = _normalise_text(context.get("product_name"), "um produto útil")
    niche = _normalise_text(context.get("niche"), "público geral")
    platform = _normalise_text(context.get("platform"), "TikTok e YouTube Shorts")
    goal = _normalise_text(context.get("goal"), "apresentar uma solução com clareza")
    return product, niche, platform, goal


def _local_output(spec: AgentSpec, context: dict[str, Any]) -> dict[str, Any]:
    product, niche, platform, goal = _project_context(context)
    tone = _normalise_text(context.get("tone"), "direto e demonstrativo")
    duration = max(6, min(int(context.get("duration_seconds") or 24), 900))

    if spec.output_contract == "strategy":
        return {
            "audience": niche,
            "angle": f"Demonstração prática de como {product} ajuda a {goal}",
            "tone": tone,
            "retention_plan": ["mostrar o problema nos 2 primeiros segundos", "demonstrar uma ação concreta", "encerrar com CTA claro e não enganoso"],
            "test_hypotheses": ["hook baseado em problema", "hook baseado em demonstração", "hook baseado em comparação honesta"],
            "platform_notes": f"Formato vertical otimizado para {platform}.",
        }
    if spec.output_contract == "script":
        scene_count = 5 if duration >= 20 else 3
        base = [
            ("Hook", f"Você ainda resolve isso do jeito mais difícil?"),
            ("Contexto", f"Este é o {product} e o problema que ele pode simplificar."),
            ("Demonstração", "Veja a ação principal em poucos segundos, sem promessa impossível."),
            ("Benefício", "O ganho é mais clareza e praticidade na rotina."),
            ("CTA", "Confira os detalhes e decida se faz sentido para você."),
        ]
        scenes = []
        each = round(duration / scene_count, 2)
        for index, (label, text) in enumerate(base[:scene_count], start=1):
            scenes.append({
                "id": f"scene-{index}",
                "label": label,
                "text": text,
                "duration_seconds": each,
                "visual_prompt": f"{product}, demonstração realista, enquadramento vertical 9:16, sem texto na imagem",
                "caption": text,
            })
        return {"title": f"{product}: demonstração rápida", "scenes": scenes, "platform": platform, "disclosure": "Conteúdo promocional: verifique detalhes antes de comprar."}
    if spec.output_contract == "visual":
        return {
            "visual_identity": {"palette": ["#0B1220", "#22D3EE", "#A7F3D0"], "font": "DejaVu Sans Bold", "style": "limpo, contrastado e demonstrativo"},
            "image_prompts": [f"Foto de produto {product} em uso por uma pessoa adulta, iluminação natural, composição vertical 9:16"],
            "negative_prompts": ["logos falsos", "texto ilegível", "antes e depois enganoso", "marcas d'água de terceiros"],
            "continuity": "Manter o produto, a paleta e o enquadramento consistentes entre as cenas.",
        }
    if spec.output_contract == "edit_recipe":
        return {
            "canvas": {"width": 1080, "height": 1920, "fps": 30, "max_duration_seconds": 900},
            "cuts": "corte ou mudança visual a cada 1,5–3,5 segundos quando houver material suficiente",
            "text_safe_area": {"top": 180, "bottom": 300, "left": 80, "right": 80},
            "transitions": ["hard_cut", "fade_short"],
            "audio_mix": {"voice_db": 0, "music_db": -18, "ducking": True},
            "export_presets": ["tiktok_9_16", "youtube_shorts_9_16"],
        }
    if spec.output_contract == "voice_caption":
        return {
            "voice_profile": {"language": "pt-BR", "pace": "natural", "tone": "claro e confiável"},
            "caption_style": {"max_words_per_line": 5, "max_lines": 2, "highlight_keywords": True, "position": "safe_center"},
            "accessibility": ["legendas sempre ligadas no arquivo exportado", "contraste alto", "não depender apenas da cor"],
        }
    if spec.output_contract == "thumbnail":
        return {
            "headline": f"{product}: vale a pena?",
            "subheadline": "Veja a demonstração",
            "composition": "produto grande em primeiro plano, fundo simples, contraste alto e espaço seguro para interface",
            "prompt": f"Capa vertical sobre {product}, produto em destaque, expressão de curiosidade, fundo limpo, sem texto gerado na imagem",
            "text_overlay": "Aplicar texto no editor, não no gerador de imagem.",
        }
    if spec.output_contract == "analytics":
        metrics = context.get("metrics") or {}
        return _analytics_fallback(metrics, product)
    if spec.output_contract == "compliance":
        return {
            "status": "review",
            "checks": [
                {"id": "claims", "status": "pass", "note": "Remover números ou resultados não comprovados."},
                {"id": "copyright", "status": "review", "note": "Usar apenas mídia própria ou licenciada."},
                {"id": "disclosure", "status": "pass", "note": "Indicar conteúdo promocional quando houver intenção comercial."},
                {"id": "platform", "status": "pass", "note": "Exportar em 9:16 e manter texto fora das áreas de interface."},
            ],
            "blocking_issues": [],
        }
    return {"message": f"Agente {spec.name} executado em modo local.", "product": product}


def _analytics_fallback(metrics: dict[str, Any], product: str) -> dict[str, Any]:
    impressions = int(metrics.get("impressions") or 0)
    views = int(metrics.get("views") or impressions)
    clicks = int(metrics.get("clicks") or 0)
    watch_time = float(metrics.get("avg_watch_time_seconds") or 0)
    duration = float(metrics.get("duration_seconds") or 0)
    ctr = clicks / impressions if impressions else 0.0
    completion = watch_time / duration if duration else 0.0
    recommendations: list[str] = []
    if impressions < 100:
        recommendations.append("Amostra pequena: não trocar o conceito com base em poucas impressões.")
    if duration and completion < 0.35:
        recommendations.append("Testar um hook mais visual e reduzir a introdução antes de alterar o CTA.")
    if impressions and ctr < 0.01:
        recommendations.append("Testar duas capas ou primeiras cenas com promessa mais específica e honesta.")
    if not recommendations:
        recommendations.append("Manter o conceito e testar apenas uma variável por vez.")
    return {
        "product": product,
        "views": views,
        "impressions": impressions,
        "clicks": clicks,
        "ctr": round(ctr, 4),
        "completion_rate_proxy": round(min(max(completion, 0.0), 1.0), 4),
        "recommendations": recommendations,
        "confidence": "low" if impressions < 100 else "medium" if impressions < 1000 else "high",
    }


def _provider_from_env() -> AgentProvider:
    provider = os.getenv("NEXUS_AI_PROVIDER", "local").strip().lower()
    if provider in {"openai", "openai-compatible", "remote"}:
        api_key = os.getenv("NEXUS_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if api_key:
            return OpenAICompatibleProvider(api_key, os.getenv("NEXUS_OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE"))
    return LocalProvider()


class AgentOrchestrator:
    """Executa agentes, aplica fallback e devolve histórico serializável."""

    def __init__(self, provider: AgentProvider | None = None):
        self.provider = provider or _provider_from_env()

    def run(self, agent_id: str, context: dict[str, Any]) -> AgentResult:
        if agent_id not in AGENT_SPECS:
            raise KeyError(f"Agente desconhecido: {agent_id}")
        spec = AGENT_SPECS[agent_id]
        provider_name = getattr(self.provider, "name", "custom")
        try:
            output = self.provider.complete(spec, context)
            return AgentResult(
                agent_id=agent_id,
                provider=provider_name,
                model=_model_for(spec),
                output=output,
                used_fallback=provider_name == "local",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as exc:
            fallback = LocalProvider().complete(spec, context)
            return AgentResult(
                agent_id=agent_id,
                provider="local-fallback",
                model=_model_for(spec),
                output=fallback,
                used_fallback=True,
                created_at=datetime.now(timezone.utc).isoformat(),
                error=str(exc),
            )


def list_agents() -> list[dict[str, Any]]:
    return [asdict(spec) for spec in AGENT_SPECS.values()]


__all__ = ["AGENT_SPECS", "AgentOrchestrator", "AgentResult", "AgentSpec", "list_agents"]
