from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st


def _is_valid_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _card(title: str, variant: str, asset_path: str | None, asset_url: str | None, description: str, cta: str, link: str, *, is_video: bool = False) -> None:
    badge = "Teste de retenção" if is_video else "Controle"
    st.markdown(f"**{variant} · {title}**  \n`{badge}`")
    if asset_path and os.path.exists(asset_path):
        if is_video:
            st.video(asset_path, width="stretch")
        else:
            st.image(asset_path, width="stretch")
    elif asset_url and _is_valid_url(asset_url):
        if is_video:
            st.video(asset_url)
        else:
            st.image(asset_url, width="stretch")
    else:
        st.warning("Criativo ainda não disponível para pré-visualização.")
    st.caption(description)
    st.link_button(cta, link, use_container_width=True)


def exibir_previa_comparativa(campaign: dict | None = None) -> None:
    """Mostra a prévia antes da autorização de publicação.

    A função não publica. Ela apenas apresenta os dois formatos e exige que o
    usuário marque a revisão antes de liberar um botão de publicação externo.
    """
    data = campaign or {}
    link = data.get("official_affiliate_url") or st.session_state.get("link_final_afiliado") or st.session_state.get("sel_link") or ""
    product = data.get("product_name") or st.session_state.get("sel_nome") or "Produto sem nome"
    image_path = data.get("image_path") or st.session_state.get("image_path_local")
    video_path = data.get("video_path") or st.session_state.get("video_path_local")
    image_url = data.get("image_url") or st.session_state.get("img_real_url")
    video_url = data.get("video_url") or st.session_state.get("nexus_video_demo")
    image_description = data.get("image_description") or f"{product}. Verifique a oferta oficial no Mercado Livre."
    video_description = data.get("video_description") or f"Gancho, demonstração e CTA para {product}."
    cta = data.get("cta") or "Ver oferta oficial"

    st.markdown("### 👁️ Prévia de publicação: Imagem A vs. Vídeo B")
    if not _is_valid_url(link):
        st.error("O destino oficial do afiliado não está configurado. A publicação fica bloqueada.")
        return

    st.info("O link é apenas pré-visualizado nesta etapa. A publicação só deve ser autorizada depois da conferência.")
    st.markdown(f"**Produto:** {product}  \n**Destino oficial:** `{link}`")
    left, right = st.columns(2)
    with left:
        _card("Imagem estática", "Imagem A", image_path, image_url, image_description, cta, link)
    with right:
        _card("Vídeo curto", "Vídeo B", video_path, video_url, video_description, cta, link, is_video=True)

    st.divider()
    reviewed = st.checkbox("Confirmei que o produto, o criativo e o link oficial correspondem.", key="preview_review_confirmed")
    if not reviewed:
        st.warning("A publicação permanece bloqueada até a revisão.")
    else:
        st.success("Prévia aprovada. O módulo de publicação pode ser liberado por uma ação explícita.")
