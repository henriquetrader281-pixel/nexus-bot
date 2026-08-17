from __future__ import annotations

from pathlib import Path

import streamlit as st

import campaign_state
from media_pipeline import generate_campaign_media


GOOGLE_LABS_URL = "https://labs.google/fx/pt/tools/flow/project/b7c52242-fa5a-4370-9975-61cc86da1483"


def _make_prompt(campaign: dict) -> str:
    product = campaign.get("product_name", "produto selecionado")
    marketplace = campaign.get("marketplace", "Mercado Livre")
    trend = (campaign.get("trends") or ["conteúdo de demonstração"])[0]
    return (
        f"Commercial product video for {product}, sold through {marketplace}. "
        f"Use the real product reference image. Trend angle: {trend}. "
        "0-3s: show the pain immediately; 3-10s: demonstrate the product in use; "
        "10-15s: show a clear official-offer CTA. Photorealistic, vertical 9:16, "
        "4K texture, cinematic lighting, clean product details, no invented product features."
    )


def _render_saved_media(campaign: dict) -> None:
    image_path = campaign.get("image_path")
    video_path = campaign.get("video_path")
    col_image, col_video = st.columns(2)
    with col_image:
        st.markdown("#### Imagem A · Controle")
        if image_path and Path(str(image_path)).is_file():
            st.image(str(image_path), use_container_width=True)
            with open(str(image_path), "rb") as file:
                st.download_button("Baixar Imagem A", file, file_name=Path(str(image_path)).name, mime="image/jpeg")
        else:
            st.info("A Imagem A ainda não foi gerada.")
    with col_video:
        st.markdown("#### Vídeo B · Teste de retenção")
        if video_path and Path(str(video_path)).is_file():
            st.video(str(video_path))
            with open(str(video_path), "rb") as file:
                st.download_button("Baixar Vídeo B", file, file_name=Path(str(video_path)).name, mime="video/mp4")
        else:
            st.info("O Vídeo B ainda não foi gerado.")


def exibir_estudio(miny=None, motor_ia=None):
    st.markdown("### 🎬 Estúdio Automatizado Nexus | Campanha Única")
    campaign = campaign_state.get_campaign()
    product = campaign.get("product_name")

    if not product:
        st.warning("Selecione ou mine um produto no Agente, Scanner, Trends ou Radar antes de abrir o Estúdio.")
        return

    st.success(f"Campanha sincronizada: **{product}** · {campaign.get('marketplace', 'Mercado Livre')}")
    st.caption(f"Dor: {campaign.get('pain', 'não definida')} | Link oficial: {campaign.get('official_affiliate_url', 'não definido')}")

    copy_text = campaign.get("copy_final") or campaign.get("copy") or ""
    if copy_text:
        with st.expander("Copy e roteiro sincronizados", expanded=False):
            edited_copy = st.text_area("Copy usada no criativo e na publicação", value=copy_text, height=180, key="studio_copy_editor")
            if st.button("Guardar copy na campanha", key="studio_save_copy"):
                campaign = campaign_state.set_campaign(copy=edited_copy, copy_final=edited_copy)
                st.success("Copy guardada e enviada para a Central de Disparo.")

    st.markdown("#### Produção de mídia")
    st.info("O Nexus baixa a imagem pública associada ao link oficial e produz localmente uma Imagem A e um Vídeo B vertical. O Google Labs fica como opção adicional, não como etapa obrigatória.")
    col1, col2 = st.columns(2)
    with col1:
        generate_button = st.button("🖼️ GERAR IMAGEM A + VÍDEO B", type="primary", use_container_width=True)
    with col2:
        voice_button = st.button("🎙️ GERAR VOZ + CRIATIVOS", use_container_width=True)

    if voice_button:
        with st.spinner("Gerando narração e montando os criativos..."):
            import tts_engine
            voice = tts_engine.gerar_narração_ia(copy_text or f"Conheça {product}.")
            if not voice.get("success"):
                st.error(f"Falha na narração: {voice.get('error')}")
            else:
                campaign = campaign_state.set_campaign(audio_path=voice["audio_path"])
                generate_button = True
                st.success("Narração produzida e anexada à campanha.")

    if generate_button:
        with st.spinner("Baixando a referência real e renderizando a Imagem A e o Vídeo B..."):
            try:
                campaign = campaign_state.get_campaign()
                manifest = generate_campaign_media(campaign)
                campaign = campaign_state.set_campaign(
                    image_path=manifest["image_a"],
                    video_path=manifest["video_b"],
                    image_url=manifest["product"].get("image_url"),
                    media_manifest=manifest,
                    prompt=_make_prompt(campaign),
                )
                st.success("Imagem A e Vídeo B gerados e enviados para a Central de Disparo.")
            except Exception as exc:
                st.error(f"Não foi possível gerar os criativos: {exc}")

    campaign = campaign_state.get_campaign()
    if campaign.get("image_path") or campaign.get("video_path"):
        _render_saved_media(campaign)

    st.divider()
    st.markdown("#### Prompt opcional para Google Labs")
    prompt = campaign.get("prompt") or _make_prompt(campaign)
    st.code(prompt, language="text")
    if st.button("Guardar prompt na campanha", key="studio_save_prompt"):
        campaign_state.set_campaign(prompt=prompt)
        st.success("Prompt guardado e disponível para a Central de Disparo.")
    st.link_button("Abrir Google Labs em nova aba", GOOGLE_LABS_URL)
