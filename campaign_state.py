"""Fonte única de verdade para o fluxo de campanha do Nexus.

As abas antigas continuam a ler algumas chaves legadas de ``st.session_state``.
Este módulo mantém essas chaves sincronizadas com ``nexus_campaign`` para que a
seleção feita numa aba apareça imediatamente nas restantes.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import streamlit as st


CAMPAIGN_KEY = "nexus_campaign"


def _clean(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _normalise_product(value: Any) -> str | None:
    value = _clean(value)
    if value is None:
        return None
    text = str(value).replace("NOME:", "").replace("Produto:", "").strip()
    if "|" in text:
        text = text.split("|", 1)[0].strip()
    return text or None


def _legacy_campaign() -> dict[str, Any]:
    state = st.session_state
    data: dict[str, Any] = {}
    aliases = {
        "product_name": state.get("sel_nome"),
        "pain": state.get("sel_dor"),
        "official_affiliate_url": state.get("sel_link") or state.get("link_final_afiliado"),
        "affiliate_url": state.get("link_final_afiliado") or state.get("sel_link"),
        "copy": state.get("copy_final_pronta") or state.get("copy_ativa"),
        "image_url": state.get("img_real_url") or state.get("nexus_media_url"),
        "image_path": state.get("image_path_local"),
        "source_image_path": state.get("source_image_path_local"),
        "video_path": state.get("video_path_local"),
        "video_source_url": state.get("nexus_video_demo"),
        "audio_path": state.get("audio_path_local"),
        "prompt": state.get("prompt_4k"),
        "script": state.get("roteiro_nexus"),
        "marketplace": state.get("mkt_global", "Mercado Livre"),
        "keywords": state.get("leads_keywords"),
        "seo": state.get("seo_dados"),
        "trends": state.get("real_trends"),
        "leads": state.get("leads_encontrados"),
        "source": state.get("campaign_source"),
    }
    for key, value in aliases.items():
        value = _clean(value)
        if value is not None:
            data[key] = value
    if data.get("product_name"):
        data["product_name"] = _normalise_product(data["product_name"])
    return data


def get_campaign() -> dict[str, Any]:
    """Retorna uma cópia da campanha atual, migrando chaves legadas quando necessário."""
    current = st.session_state.get(CAMPAIGN_KEY)
    if isinstance(current, dict):
        data = deepcopy(current)
        legacy = _legacy_campaign()
        for key, value in legacy.items():
            data.setdefault(key, value)
        return data
    return _legacy_campaign()


def set_campaign(**updates: Any) -> dict[str, Any]:
    """Atualiza a campanha e espelha os campos nas chaves antigas da aplicação."""
    data = get_campaign()
    incoming_product = _normalise_product(updates.get("product_name"))
    current_product = _normalise_product(data.get("product_name"))
    if incoming_product and current_product and incoming_product != current_product:
        # Novo produto = nova campanha. Não herdar ativos nem links da anterior.
        data = {"product_name": incoming_product}
        for key in ("marketplace", "pain", "niche", "source", "trend_term"):
            if updates.get(key) is not None:
                data[key] = updates[key]
        for key in ("sel_link", "link_final_afiliado", "copy_ativa", "copy_final_pronta", "image_path_local", "video_path_local", "audio_path_local", "img_real_url", "nexus_video_demo", "prompt_4k", "roteiro_nexus", "nexus_media_url", "nexus_media_ready", "leads_keywords", "leads_encontrados", "seo_dados", "real_trends", "trends_gringa", "nexus_estrat", "res_arsenal"):
            st.session_state.pop(key, None)
    for key, value in updates.items():
        if value is not None:
            data[key] = value
    if data.get("product_name") is not None:
        data["product_name"] = _normalise_product(data["product_name"])
    if data.get("official_affiliate_url") and not data.get("affiliate_url"):
        data["affiliate_url"] = data["official_affiliate_url"]
    if data.get("affiliate_url") and not data.get("official_affiliate_url"):
        data["official_affiliate_url"] = data["affiliate_url"]

    st.session_state[CAMPAIGN_KEY] = deepcopy(data)
    _sync_legacy(data)
    return deepcopy(data)


def _sync_legacy(data: dict[str, Any]) -> None:
    state = st.session_state
    mapping = {
        "product_name": "sel_nome",
        "pain": "sel_dor",
        "official_affiliate_url": "sel_link",
        "affiliate_url": "link_final_afiliado",
        "copy": "copy_ativa",
        "copy_final": "copy_final_pronta",
        "image_url": "img_real_url",
        "image_path": "image_path_local",
        "source_image_path": "source_image_path_local",
        "video_path": "video_path_local",
        "video_source_url": "nexus_video_demo",
        "audio_path": "audio_path_local",
        "prompt": "prompt_4k",
        "script": "roteiro_nexus",
        "source": "campaign_source",
        "keywords": "leads_keywords",
        "seo": "seo_dados",
        "trends": "real_trends",
        "leads": "leads_encontrados",
    }
    for source, target in mapping.items():
        if data.get(source) is not None:
            state[target] = data[source]
    if data.get("copy") and not data.get("copy_final"):
        state["copy_final_pronta"] = data["copy"]
    if data.get("image_url"):
        state["nexus_media_url"] = data["image_url"]
        state["nexus_media_ready"] = True
    state["nexus_campaign_ready"] = bool(data.get("product_name"))


def set_from_product(product: dict[str, Any], *, source: str = "miner") -> dict[str, Any]:
    """Converte a descoberta para o contrato de campanha sem chamar permalink de afiliado."""
    official_url = product.get("official_affiliate_url") or product.get("affiliate_url")
    source_url = product.get("product_source_url") or product.get("permalink") or product.get("link_ml") or product.get("link")
    return set_campaign(
        product_name=product.get("produto") or product.get("product_name") or product.get("title"),
        pain=product.get("dificuldade") or product.get("dor") or product.get("pain"),
        official_affiliate_url=official_url,
        affiliate_url=official_url,
        product_source_url=source_url,
        copy=product.get("copy"),
        image_url=product.get("imagem") or product.get("image_url"),
        source_image_url=product.get("imagem") or product.get("image_url"),
        image_verified=product.get("image_verified"),
        image_source=product.get("image_source"),
        product_external_id=product.get("product_external_id") or product.get("id"),
        price=product.get("price"),
        query=product.get("query"),
        video_source_url=product.get("video_demo") or product.get("video_source_url"),
        marketplace=product.get("marketplace") or st.session_state.get("mkt_global", "Mercado Livre"),
        niche=product.get("nicho") or product.get("niche"),
        source=product.get("source") or source,
    )


def clear_campaign() -> None:
    """Limpa apenas o estado da campanha, preservando autenticação e preferências."""
    for key in [CAMPAIGN_KEY, "nexus_campaign_ready"]:
        st.session_state.pop(key, None)
    for key in (
        "sel_nome", "sel_dor", "sel_link", "link_final_afiliado", "copy_ativa",
        "copy_final_pronta", "img_real_url", "image_path_local", "source_image_path_local", "video_path_local",
        "nexus_video_demo", "audio_path_local", "prompt_4k", "roteiro_nexus",
        "nexus_media_url", "nexus_media_ready", "campaign_source", "media_manifest",
        "leads_keywords", "leads_encontrados", "seo_dados", "scan_results",
        "real_trends", "trends_gringa", "nexus_estrat", "res_arsenal",
    ):
        st.session_state.pop(key, None)


__all__ = ["get_campaign", "set_campaign", "set_from_product", "clear_campaign"]
