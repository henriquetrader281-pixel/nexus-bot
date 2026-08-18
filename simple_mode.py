from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import requests
import streamlit as st

import campaign_state
from media_pipeline import generate_campaign_media


SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"
STOPWORDS = {
    "a", "o", "as", "os", "de", "do", "da", "dos", "das", "para", "por", "com",
    "sem", "uma", "um", "e", "em", "no", "na", "nos", "nas", "que", "se", "mais",
}


def _secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.environ.get(name)


def buscar_produtos_mercado_livre(query: str, limit: int = 8) -> list[dict[str, Any]]:
    response = requests.get(
        SEARCH_URL,
        params={"q": query, "limit": limit},
        headers={"User-Agent": "NexusBot-SimpleMode/1.0"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    results = []
    for item in data.get("results", []):
        results.append({
            "id": item.get("id"),
            "title": item.get("title") or "Produto Mercado Livre",
            "permalink": item.get("permalink") or "",
            "image_url": item.get("secure_thumbnail") or item.get("thumbnail"),
            "price": item.get("price"),
        })
    return results


def analisar_palavras_chave(product: str, pain: str, raw_keywords: str = "", trends: list[str] | None = None) -> dict[str, Any]:
    source = " ".join([product, pain, raw_keywords, " ".join(trends or [])]).lower()
    words = re.findall(r"[a-záàâãéêíóôõúç0-9]{4,}", source, flags=re.IGNORECASE)
    keywords: list[str] = []
    for word in words:
        if word not in STOPWORDS and word not in keywords:
            keywords.append(word)
    keywords = keywords[:12] or ["solução prática", "oferta oficial", "produto útil"]
    focus = keywords[0]
    pain_clean = pain.strip() or "perder tempo com este problema"
    hooks = [
        f"Você ainda perde tempo com {pain_clean.lower()}?",
        f"O que quase ninguém procura sobre {focus}: uma solução simples para o dia a dia.",
        f"Pare de improvisar: veja como {product.strip() or 'este produto'} pode facilitar a rotina.",
    ]
    return {"keywords": keywords, "hooks": hooks, "focus": focus}


def _fallback_copy(product: str, pain: str, analysis: dict[str, Any], official_url: str = "") -> str:
    hook = analysis["hooks"][0]
    focus = analysis["focus"]
    return (
        f"{hook}\n\n"
        f"Se {pain.lower().strip() or 'este problema faz parte da sua rotina'}, você não precisa continuar a improvisar. "
        f"O {product} foi selecionado por unir praticidade, uso simples e uma solução objetiva para o dia a dia.\n\n"
        f"A ideia é ganhar tempo e reduzir a fricção sem prometer milagres: veja os detalhes, preço e disponibilidade na oferta oficial. "
        f"Palavra-chave do gancho: {focus}.\n\n"
        f"Comente QUERO ou acesse a oferta oficial para conferir o produto."
    )


def gerar_copy(campaign: dict[str, Any], analysis: dict[str, Any]) -> tuple[str, str | None]:
    product = campaign.get("product_name", "produto selecionado")
    pain = campaign.get("pain") or "uma dificuldade recorrente na rotina"
    prompt = f"""Crie uma copy de afiliado em português do Brasil para {product}.
Dor observada: {pain}
Palavras-chave: {', '.join(analysis['keywords'])}
Ganchos candidatos: {' | '.join(analysis['hooks'])}

Use AIDA, linguagem natural, sem promessas falsas, sem inventar preço, desconto, avaliações ou características não confirmadas.
Entregue: um gancho de 1 frase, desenvolvimento curto, benefício verificável e CTA para comentar QUERO ou abrir a oferta oficial.
Não inclua markdown, títulos técnicos ou explicações sobre a tarefa."""
    api_key = _secret("GROQ_API_KEY")
    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            result = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Você é um copywriter de performance ético e natural."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.75,
                max_tokens=500,
            )
            content = result.choices[0].message.content.strip()
            if content:
                return content, None
        except Exception as exc:
            return _fallback_copy(product, pain, analysis), f"Groq indisponível; fallback aplicado: {exc}"
    return _fallback_copy(product, pain, analysis), "Copy determinística aplicada. Configure GROQ_API_KEY para variações IA."


def _save_upload(uploaded_file, product_name: str) -> str | None:
    if uploaded_file is None:
        return None
    folder = Path(".nexus_media") / "manual_uploads"
    folder.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9À-ÿ]+", "_", product_name or "produto").strip("_")[:50] or "produto"
    suffix = Path(uploaded_file.name).suffix.lower() or ".jpg"
    target = folder / f"{safe}{suffix}"
    target.write_bytes(uploaded_file.getbuffer())
    return str(target)


def _apply_input(product: str, pain: str, official_url: str, image_url: str, analysis: dict[str, Any] | None = None) -> dict[str, Any]:
    campaign = campaign_state.get_campaign()
    updates: dict[str, Any] = {
        "product_name": product.strip(),
        "pain": pain.strip() or "Necessidade identificada no mercado",
        "official_affiliate_url": official_url.strip() or None,
        "image_url": image_url.strip() or None,
        "keywords": analysis.get("keywords") if analysis else campaign.get("keywords"),
        "hooks": analysis.get("hooks") if analysis else campaign.get("hooks"),
        "source": "modo_simples",
    }
    if campaign.get("product_source_url"):
        updates["product_source_url"] = campaign["product_source_url"]
    return campaign_state.set_campaign(**updates)


def _render_simple_media(campaign: dict[str, Any]) -> None:
    image_path = campaign.get("image_path")
    video_path = campaign.get("video_path")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Imagem com texto e CTA")
        if image_path and Path(str(image_path)).is_file():
            st.image(str(image_path), use_container_width=True)
            with open(str(image_path), "rb") as file:
                st.download_button("Baixar Imagem", file, file_name=Path(str(image_path)).name, mime="image/jpeg", key="simple_download_image")
        else:
            st.info("A imagem ainda não foi gerada.")
    with col2:
        st.markdown("#### Vídeo com áudio e legenda")
        if video_path and Path(str(video_path)).is_file():
            st.video(str(video_path))
            with open(str(video_path), "rb") as file:
                st.download_button("Baixar Vídeo", file, file_name=Path(str(video_path)).name, mime="video/mp4", key="simple_download_video")
        else:
            st.info("O vídeo ainda não foi gerado.")


def exibir_modo_simples() -> None:
    st.header("🚀 Modo Simples · Criar Campanha")
    st.caption("Busque ou cole um produto, escolha a imagem, analise os ganchos e gere copy, imagem, áudio, legenda e vídeo numa única campanha.")
    campaign = campaign_state.get_campaign()

    with st.container(border=True):
        st.markdown("#### 1. Encontrar o produto")
        source = st.radio("Entrada", ["Buscar no Mercado Livre", "Colar link oficial"], horizontal=True, key="simple_source")
        if source == "Buscar no Mercado Livre":
            query = st.text_input("O que você procura?", placeholder="ex.: organizador de cozinha, power bank, luminária para monitor", key="simple_search_query")
            if st.button("🔎 BUSCAR PRODUTOS", type="primary", key="simple_search_button"):
                if not query.strip():
                    st.warning("Digite um produto ou problema para pesquisar.")
                else:
                    try:
                        st.session_state.simple_search_results = buscar_produtos_mercado_livre(query)
                    except Exception as exc:
                        st.error(f"Não foi possível consultar o Mercado Livre agora: {exc}")
            results = st.session_state.get("simple_search_results", [])
            if results:
                labels = [f"{item['title']} · R$ {item['price']}" if item.get("price") else item["title"] for item in results]
                selected_index = st.selectbox("Selecione um resultado", range(len(labels)), format_func=lambda index: labels[index], key="simple_result_select")
                selected = results[selected_index]
                if st.button("✅ USAR PRODUTO SELECIONADO", key="simple_use_result"):
                    campaign_state.set_campaign(
                        product_name=selected["title"],
                        pain=f"Encontrar uma solução melhor para {selected['title'].lower()}",
                        product_source_url=selected.get("permalink"),
                        image_url=selected.get("image_url"),
                        price=selected.get("price"),
                        marketplace="Mercado Livre",
                        source="mercado_livre_search",
                    )
                    st.success("Produto selecionado. Agora associe o link oficial de afiliado para liberar a publicação.")
                    st.rerun()
        else:
            st.info("Cole o link específico gerado no Portal do Afiliado. A URL da Vitrine geral não identifica o produto.")

        product = st.text_input("Produto", value=campaign.get("product_name", ""), key="simple_product_input")
        pain = st.text_input("Dor ou desejo principal", value=campaign.get("pain", ""), key="simple_pain_input")
        official_url = st.text_input("Link oficial do Mercado Livre para rastrear a oferta", value=campaign.get("official_affiliate_url", ""), placeholder="https://meli.la/...", key="simple_official_url")
        image_url = st.text_input("URL pública da imagem (opcional)", value=campaign.get("image_url", ""), placeholder="https://...jpg", key="simple_image_url")
        upload = st.file_uploader("Ou suba uma imagem do produto", type=["jpg", "jpeg", "png", "webp"], key="simple_image_upload")
        if upload is not None and product:
            saved_upload = _save_upload(upload, product)
            if saved_upload:
                campaign = campaign_state.set_campaign(source_image_path=saved_upload, product_name=product, source="modo_simples_upload")
                st.success("Imagem manual guardada como fallback para o criativo.")

        keywords_input = st.text_input("Palavras-chave, tendência ou gancho desejado", value=", ".join(campaign.get("keywords", []) or []), key="simple_keywords_input")
        save_col, analyse_col = st.columns(2)
        with save_col:
            save_input = st.button("💾 GUARDAR CAMPANHA", key="simple_save_input")
        with analyse_col:
            analyse_button = st.button("🧠 ANALISAR PALAVRAS-CHAVE + GANCHOS", type="primary", key="simple_analyse")
        if save_input or analyse_button:
            if not product.strip():
                st.error("Informe ou busque um produto antes de guardar.")
            else:
                analysis = analisar_palavras_chave(product, pain, keywords_input, campaign.get("trends"))
                campaign = _apply_input(product, pain, official_url, image_url, analysis)
                if analyse_button:
                    st.success("Palavras-chave analisadas e ganchos preparados para a copy e o vídeo.")

    campaign = campaign_state.get_campaign()
    if not campaign.get("product_name"):
        st.info("Comece buscando um produto ou colando os dados acima.")
        return

    with st.container(border=True):
        st.markdown(f"#### 2. Campanha ativa: {campaign['product_name']}")
        st.caption(f"Dor: {campaign.get('pain', 'não definida')} · Marketplace: {campaign.get('marketplace', 'Mercado Livre')}")
        hooks = campaign.get("hooks") or analisar_palavras_chave(campaign["product_name"], campaign.get("pain", ""), ", ".join(campaign.get("keywords", []) or []))["hooks"]
        st.markdown("**Ganchos encontrados:**")
        for hook in hooks[:3]:
            st.write(f"• {hook}")
        if st.button("✨ GERAR CAMPANHA COMPLETA", type="primary", use_container_width=True, key="simple_generate_all"):
            with st.spinner("Gerando copy, áudio, Imagem A e Vídeo B..."):
                try:
                    analysis = analisar_palavras_chave(campaign["product_name"], campaign.get("pain", ""), ", ".join(campaign.get("keywords", []) or []), campaign.get("trends"))
                    copy_text, copy_warning = gerar_copy(campaign, analysis)
                    campaign = campaign_state.set_campaign(copy=copy_text, copy_final=copy_text, hooks=analysis["hooks"], keywords=analysis["keywords"])
                    if copy_warning:
                        st.info(copy_warning)
                    try:
                        import tts_engine
                        voice = tts_engine.gerar_narração_ia(copy_text)
                    except Exception as voice_exc:
                        voice = {"success": False, "error": str(voice_exc)}
                    if voice.get("success"):
                        campaign = campaign_state.set_campaign(audio_path=voice["audio_path"])
                    else:
                        st.warning(f"Áudio não disponível; o vídeo será gerado com legenda: {voice.get('error', 'fallback sem áudio')}.")
                    campaign = campaign_state.get_campaign()
                    manifest = generate_campaign_media(campaign)
                    campaign_state.set_campaign(
                        image_path=manifest["image_a"],
                        video_path=manifest["video_b"],
                        image_url=manifest["product"].get("image_url") or campaign.get("image_url"),
                        media_manifest=manifest,
                        script=hooks,
                    )
                    st.success("Campanha completa criada. Reveja a prévia antes de publicar.")
                except Exception as exc:
                    st.error(f"Não foi possível concluir a campanha: {exc}")

    campaign = campaign_state.get_campaign()
    if campaign.get("copy_final"):
        with st.expander("📝 Copy AIDA gerada", expanded=True):
            st.text_area("Copy", campaign["copy_final"], height=210, key="simple_copy_preview")
    if campaign.get("image_path") or campaign.get("video_path"):
        _render_simple_media(campaign)
    if campaign.get("official_affiliate_url"):
        st.success("Link oficial associado. A campanha pode seguir para a Central de Disparo.")
        st.link_button("Abrir oferta oficial", campaign["official_affiliate_url"])
    else:
        st.warning("A campanha pode gerar criativos com o resultado da busca, mas precisa do link oficial de afiliado antes da publicação.")
