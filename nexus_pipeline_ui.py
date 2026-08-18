"""Esteira principal do Nexus: produto -> pacote -> link manual -> Pinterest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

import campaign_queue
import campaign_state
from media_pipeline import generate_campaign_media
from simple_mode import (
    _save_upload,
    analisar_palavras_chave,
    buscar_produtos_mercado_livre,
    gerar_copy,
)


def _safe_file(path_value: Any) -> Path | None:
    if not path_value:
        return None
    path = Path(str(path_value))
    return path if path.is_file() else None


PAIN_RULES = (
    (("power bank", "carregador", "bateria", "cabo"), "ficar sem bateria quando precisa do celular e perder tempo procurando uma tomada"),
    (("organizador", "cozinha", "armário", "gaveta"), "perder tempo com desorganização e não encontrar o que precisa"),
    (("luminária", "monitor", "led", "luz"), "cansar a visão e trabalhar com iluminação desconfortável"),
    (("massage", "massagem", "muscular", "relaxante"), "terminar o dia com tensão muscular e dificuldade para relaxar"),
    (("fone", "headphone", "bluetooth", "ruído"), "ter distrações e dificuldade para ouvir com clareza na rotina"),
    (("beleza", "cosmético", "maquiagem", "cabelo"), "gastar tempo na rotina de cuidados sem praticidade"),
)


def inferir_dor_produto(product_name: str, trend_term: str = "") -> str:
    text = f"{product_name} {trend_term}".lower()
    for terms, pain in PAIN_RULES:
        if any(term in text for term in terms):
            return pain
    return f"ter uma necessidade recorrente relacionada a {trend_term or product_name.lower()} e não encontrar uma solução prática"


def _keywords_for_product(product_name: str, trend_term: str = "") -> list[str]:
    values = [trend_term.strip().lower()] if trend_term.strip() else []
    values.extend(word.lower() for word in product_name.split() if len(word) >= 4)
    return list(dict.fromkeys(value for value in values if value))[:12]


def _apply_mined_product(product: dict[str, Any], trend_term: str, trend_source: str) -> None:
    campaign_state.set_from_product(product, source="main_auto_miner")
    name = product.get("produto") or product.get("title") or "Produto selecionado"
    campaign_state.set_campaign(
        pain=inferir_dor_produto(name, trend_term),
        trend_term=trend_term,
        trend_source=trend_source,
        trends=st.session_state.get("real_trends", []),
        keywords=_keywords_for_product(name, trend_term),
        image_verified=product.get("image_verified", True),
        image_source=product.get("image_source") or "thumbnail do mesmo anúncio",
    )


def _load_selected_queue() -> None:
    rows = campaign_queue.list_prepared_campaigns(limit=100)
    if not rows:
        return
    labels = [
        f"#{row['id']} · {row['product_name']} · {row.get('status', 'ready')} · {row.get('created_at', '')}"
        for row in rows
    ]
    selected = st.selectbox("Pacote guardado", labels, key="main_queue_selector")
    selected_row = rows[labels.index(selected)]
    if st.button("📂 CARREGAR PACOTE", key="main_load_queue", use_container_width=True):
        campaign_state.set_campaign(**campaign_queue.campaign_from_queue_row(selected_row))
        st.rerun()


def _mine_one_product(query: str = "") -> None:
    try:
        from real_marketplace_engine import obter_produto_real_validado
        from trends import obter_tendencias_reais

        trend_values, trend_source = obter_tendencias_reais(limit=10)
        trend_term = query.strip() or (trend_values[0] if trend_values else "produtos úteis")
        product = obter_produto_real_validado("gemini", query=trend_term)
        _apply_mined_product(product, trend_term, trend_source)
        st.success(f"Produto minerado: {product.get('produto') or product.get('title')}")
        st.info(f"Tendência usada: **{trend_term}** · fonte: {trend_source}")
        st.rerun()
    except Exception as exc:
        st.error("A mineração foi bloqueada com segurança: o Mercado Livre não devolveu um produto com imagem pública.")
        st.code(str(exc), language="text")
        st.info("Na mesma tela, informe o produto e uma imagem pública ou faça upload da imagem real para continuar sem a API.")


def _generate_package(campaign: dict[str, Any]) -> tuple[dict[str, Any], str]:
    analysis = analisar_palavras_chave(
        campaign["product_name"],
        campaign.get("pain", "Necessidade identificada no mercado"),
        ", ".join(campaign.get("keywords", []) or []),
        campaign.get("trends"),
    )
    copy_text, copy_warning = gerar_copy(campaign, analysis)
    if copy_warning:
        st.info(copy_warning)
    campaign = campaign_state.set_campaign(
        copy=copy_text,
        copy_final=copy_text,
        hooks=analysis["hooks"],
        keywords=analysis["keywords"],
        caption=analysis["caption"],
        cta_variations=analysis["cta_variations"],
        intent=analysis["intent"],
        intent_label=analysis["intent_label"],
    )

    audio_ready = False
    try:
        import tts_engine

        voice = tts_engine.gerar_narração_ia(copy_text)
    except Exception as exc:
        voice = {"success": False, "error": str(exc)}
    if voice.get("success") and voice.get("audio_path"):
        campaign = campaign_state.set_campaign(audio_path=voice["audio_path"])
        audio_ready = _safe_file(voice["audio_path"]) is not None
    else:
        st.warning(f"Áudio não disponível: {voice.get('error', 'fornecedor indisponível')}")

    media_ready = False
    try:
        campaign = campaign_state.get_campaign()
        manifest = generate_campaign_media(campaign)
        campaign = campaign_state.set_campaign(
            source_image_path=manifest.get("source_image_path"),
            image_path=manifest.get("image_a"),
            video_path=manifest.get("video_b"),
            image_url=manifest.get("product", {}).get("image_url") or campaign.get("image_url"),
            media_manifest=manifest,
        )
        media_ready = all(_safe_file(manifest.get(key)) is not None for key in ("image_a", "video_b"))
    except Exception as exc:
        st.error(f"Não foi possível concluir a mídia: {exc}")

    campaign = campaign_state.get_campaign()
    status = "ready" if audio_ready and media_ready else "needs_review"
    queue_id = campaign_queue.save_prepared_campaign(campaign, status=status)
    campaign_state.set_campaign(queue_id=queue_id, queue_status=status, publication_status="manual_only")
    return campaign_state.get_campaign(), status


def _render_package(campaign: dict[str, Any]) -> None:
    st.markdown("### 4. Pacote Pinterest pronto")
    st.caption(f"Status: **{campaign.get('queue_status', 'draft')}** · Nenhuma rede foi acionada automaticamente.")

    copy_text = campaign.get("copy_final") or campaign.get("copy") or ""
    caption = campaign.get("caption") or copy_text
    link = campaign.get("official_affiliate_url") or ""

    copy_col, link_col = st.columns([2, 1])
    with copy_col:
        st.text_area("Copy AIDA", copy_text, height=220, key=f"main_copy_{campaign.get('queue_id', 'active')}")
        pinterest_title = campaign.get("product_name", "Oferta")[:100]
        st.text_input("Título sugerido para Pinterest", value=pinterest_title, key=f"main_pinterest_title_{campaign.get('queue_id', 'active')}")
        st.text_area("Legenda para Pinterest", caption, height=150, key=f"main_caption_{campaign.get('queue_id', 'active')}")
        st.code(caption, language="text")
        st.download_button(
            "📥 BAIXAR LEGENDA .TXT",
            data=caption,
            file_name=f"legenda_{campaign.get('queue_id', 'campanha')}.txt",
            mime="text/plain",
            key=f"main_caption_download_{campaign.get('queue_id', 'active')}",
        )
    with link_col:
        st.markdown("#### Link oficial — último passo")
        manual_link = st.text_input(
            "Cole aqui o link do Portal de Afiliados",
            value=link,
            placeholder="https://meli.la/...",
            key=f"main_manual_link_{campaign.get('queue_id', 'active')}",
        )
        if st.button("🔗 ASSOCIAR LINK OFICIAL", type="primary", use_container_width=True, key="main_associate_link"):
            if not manual_link.strip().startswith(("http://", "https://")):
                st.error("Cole um URL HTTP(S) válido emitido pelo Portal de Afiliados.")
            else:
                campaign_state.set_campaign(
                    official_affiliate_url=manual_link.strip(),
                    affiliate_url=manual_link.strip(),
                )
                if campaign.get("queue_id"):
                    campaign_queue.update_prepared_campaign_link(campaign["queue_id"], manual_link.strip())
                st.success("Link associado. Agora pode copiar o pacote e publicar manualmente no Pinterest.")
                st.rerun()
        if manual_link.strip().startswith(("http://", "https://")):
            st.code(manual_link.strip(), language="text")
            st.link_button("Abrir link oficial", manual_link.strip(), use_container_width=True)
        else:
            st.warning("Aguardando apenas o link oficial para concluir o pacote.")

    image_path = _safe_file(campaign.get("image_path"))
    video_path = _safe_file(campaign.get("video_path"))
    audio_path = _safe_file(campaign.get("audio_path"))
    image_col, video_col = st.columns(2)
    with image_col:
        st.markdown("#### Imagem A")
        if image_path:
            st.image(str(image_path), use_container_width=True)
            st.download_button("Baixar Imagem A", image_path.read_bytes(), image_path.name, "image/jpeg", key=f"main_image_download_{campaign.get('queue_id', 'active')}")
        else:
            st.warning("Imagem A não encontrada.")
    with video_col:
        st.markdown("#### Vídeo B")
        if video_path:
            st.video(str(video_path))
            st.download_button("Baixar Vídeo B", video_path.read_bytes(), video_path.name, "video/mp4", key=f"main_video_download_{campaign.get('queue_id', 'active')}")
        else:
            st.warning("Vídeo B não encontrado.")
    if audio_path:
        st.audio(str(audio_path))


def exibir_esteira_principal() -> None:
    st.header("🚀 Nexus · Esteira Principal")
    st.caption("Uma única tela para minerar, produzir e deixar o conteúdo pronto. No final, falta apenas colar o link oficial e publicar manualmente no Pinterest.")

    try:
        _load_selected_queue()
    except Exception as exc:
        st.warning(f"A fila ainda não pôde ser carregada: {exc}")

    campaign = campaign_state.get_campaign()
    progress = 0.0
    if campaign.get("product_name"):
        progress = 0.25
    if campaign.get("copy_final"):
        progress = 0.50
    if campaign.get("image_path") or campaign.get("video_path"):
        progress = 0.75
    if campaign.get("official_affiliate_url"):
        progress = 1.0
    st.progress(progress, text=f"Progresso da esteira: {int(progress * 100)}%")

    with st.container(border=True):
        st.markdown("### 1. Encontrar o produto")
        search_col, auto_col = st.columns([3, 1])
        with search_col:
            query = st.text_input("Pesquisar no Mercado Livre", placeholder="ex.: power bank, organizador de cozinha, luminária", key="main_search_query")
            if st.button("📈 BUSCAR PRODUTOS EM ALTA", key="main_trend_button"):
                try:
                    from trends import obter_tendencias_reais

                    values, source = obter_tendencias_reais(limit=10)
                    st.session_state.main_trend_values = values
                    st.session_state.main_trend_source = source
                    st.success(f"{len(values)} tendências carregadas de {source}.")
                except Exception as exc:
                    st.error(f"Não foi possível carregar tendências: {exc}")
            trend_values = st.session_state.get("main_trend_values", [])
            if trend_values:
                trend_term = st.selectbox("Escolha um termo em alta", trend_values, key="main_trend_select")
                if st.button("🔎 USAR TERMO EM ALTA", key="main_use_trend"):
                    st.session_state.main_search_query = trend_term
                    st.rerun()
            if st.button("🔎 BUSCAR PRODUTOS", type="primary", key="main_search_button"):
                if not query.strip():
                    st.warning("Digite um produto ou problema para pesquisar.")
                else:
                    try:
                        st.session_state.main_search_results = buscar_produtos_mercado_livre(query)
                    except Exception as exc:
                        st.error(f"A busca foi bloqueada: {exc}")
        with auto_col:
            st.markdown("**Ou**")
            if st.button("⛏️ MINERAR AUTOMÁTICO", key="main_auto_mine", use_container_width=True):
                _mine_one_product(query)

        results = st.session_state.get("main_search_results", [])
        if results:
            labels = [f"{item['title']} · R$ {item['price']}" if item.get("price") else item["title"] for item in results]
            selected_index = st.selectbox("Resultado encontrado", range(len(labels)), format_func=lambda index: labels[index], key="main_result_select")
            selected = results[selected_index]
            if st.button("✅ USAR ESTE PRODUTO", key="main_use_product"):
                trend_term = st.session_state.get("main_search_query", query).strip()
                campaign_state.set_campaign(
                    product_name=selected["title"],
                    pain=inferir_dor_produto(selected["title"], trend_term),
                    product_source_url=selected.get("permalink"),
                    image_url=selected.get("image_url"),
                    source_image_url=selected.get("image_url"),
                    image_verified=bool(selected.get("image_url")),
                    image_source="thumbnail do resultado selecionado",
                    price=selected.get("price"),
                    marketplace="Mercado Livre",
                    trend_term=trend_term,
                    trends=st.session_state.get("main_trend_values", []),
                    keywords=_keywords_for_product(selected["title"], trend_term),
                    source="main_search",
                )
                st.rerun()

        product = st.text_input("Produto selecionado", value=campaign.get("product_name", ""), key="main_product")
        pain = st.text_input("Dor ou desejo principal", value=campaign.get("pain", ""), key="main_pain")
        image_url = st.text_input("Imagem pública opcional", value=campaign.get("image_url", ""), key="main_image_url")
        upload = st.file_uploader("Ou suba a imagem real do produto", type=["jpg", "jpeg", "png", "webp"], key="main_upload")
        if upload is not None and product:
            saved = _save_upload(upload, product)
            if saved:
                campaign_state.set_campaign(product_name=product, source_image_path=saved, source="main_upload")
                st.success("Imagem-fonte manual guardada.")
        if product and st.button("💾 CONFIRMAR PRODUTO", key="main_confirm_product"):
            campaign_state.set_campaign(product_name=product, pain=pain, image_url=image_url or None, source="main_product")
            st.rerun()

    campaign = campaign_state.get_campaign()
    if not campaign.get("product_name"):
        st.info("Comece pela pesquisa ou pela mineração automática.")
        return

    with st.container(border=True):
        st.markdown("### 2. Copy, hooks e legenda")
        analysis = analisar_palavras_chave(campaign["product_name"], campaign.get("pain", ""), ", ".join(campaign.get("keywords", []) or []), campaign.get("trends"))
        st.write("**Tendência usada:**", campaign.get("trend_term") or "a definir")
        st.write("**Dor/desejo detectado:**", campaign.get("pain") or inferir_dor_produto(campaign["product_name"], campaign.get("trend_term", "")))
        st.write("**Intenção:**", campaign.get("intent_label") or analysis["intent_label"])
        st.write("**Hooks selecionados:**", " · ".join(analysis["hooks"][:4]))
        if st.button("✨ GERAR PACOTE COMPLETO", type="primary", key="main_generate_package", use_container_width=True):
            with st.spinner("A sequência está a gerar copy, áudio, imagem e vídeo..."):
                _generate_package(campaign)
            st.success("Pacote gerado e guardado na fila.")
            st.rerun()

    campaign = campaign_state.get_campaign()
    if campaign.get("copy_final") or campaign.get("image_path") or campaign.get("video_path"):
        _render_package(campaign)
