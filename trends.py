from __future__ import annotations

import re
import time
import unicodedata
import xml.etree.ElementTree as ET

import pandas as pd
import requests
import streamlit as st
from pytrends.request import TrendReq

import campaign_state

RSS_URL = "https://trends.google.com/trending/rss?geo=BR"
FALLBACK_TRENDS = [
    "organizador de cozinha",
    "luminária para monitor",
    "power bank carregador portátil",
    "pistola de massagem muscular",
    "fone bluetooth cancelamento de ruído",
]
RSS_NAMESPACE = "{https://trends.google.com/trending/rss}"

# Termos que indicam procura comercial; são usados apenas para filtrar o feed
# geral antes de consultar anúncios. A aprovação final depende de um produto
# real com permalink e imagem devolvidos pelo Mercado Livre.
PRODUCT_MARKERS = {
    "celular", "iphone", "samsung", "xiaomi", "notebook", "computador", "monitor", "smart", "tv",
    "fone", "headphone", "bluetooth", "camera", "câmera", "relogio", "relógio", "smartwatch", "maquiagem",
    "perfume", "tenis", "tênis", "bolsa", "cadeira", "mesa", "organizador", "cozinha", "luminaria", "luminária",
    "lampada", "lâmpada", "power", "carregador", "bateria", "massagem", "fitness", "bike", "bicicleta",
    "console", "playstation", "xbox", "casa", "jardim", "ferramenta", "aspirador", "liquidificador", "cafeteira",
    "panela", "airfryer", "brinquedo", "bebe", "bebê", "moda", "desconto", "oferta", "cupom", "preco", "preço",
    "comprar", "promoção", "promocao",
}
NON_PRODUCT_MARKERS = {
    "presidente", "presidência", "presidencia", "eleição", "eleicao", "política", "politica", "deputado", "senador",
    "governo", "apac", "tempo", "previsão", "previsao", "clima", "chuva", "chuvas", "furacão", "furacao",
    "jogo", "futebol", "campeonato", "copa", "placar", "morte", "morreu", "notícia", "noticia", "novela",
    "bbb", "gloria", "glória", "malcom", "zeze", "zé", "famoso", "famosa", "celebridade", "guerra",
}


def _fold_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


def is_commercial_trend(value: str) -> bool:
    """Retorna verdadeiro apenas para sinais com indício de intenção de produto."""
    folded = _fold_text(value)
    if len(folded) < 4 or any(marker in folded for marker in NON_PRODUCT_MARKERS):
        return False
    tokens = set(re.findall(r"[a-z0-9]{3,}", folded))
    return bool(tokens.intersection({_fold_text(marker) for marker in PRODUCT_MARKERS}))


def filtrar_tendencias_comerciais(values: list[str], limit: int = 12) -> list[str]:
    filtered: list[str] = []
    for value in values:
        clean = str(value).strip()
        if clean and is_commercial_trend(clean) and clean not in filtered:
            filtered.append(clean)
        if len(filtered) >= max(1, int(limit)):
            break
    return filtered


def fetch_google_trends_rss(limit: int = 25) -> list[str]:
    """Obtém tendências atuais do feed oficial Trending Now do Google Brasil."""
    response = requests.get(
        RSS_URL,
        headers={"User-Agent": "NexusBot-Trends/1.0", "Accept": "application/rss+xml, application/xml"},
        timeout=(10, 25),
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)
    values: list[str] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        if title and title not in values:
            values.append(title)
        if len(values) >= limit:
            break
    if not values:
        raise RuntimeError("RSS do Google Trends não devolveu itens.")
    return values


def _trend_client() -> TrendReq:
    """Cria pytrends apenas como fallback compatível com urllib3 1.x/2.x."""
    try:
        return TrendReq(hl="pt-BR", tz=180, retries=2, backoff_factor=0.1, timeout=(10, 25))
    except TypeError as exc:
        if "method_whitelist" not in str(exc):
            raise
        from urllib3.util.retry import Retry

        original_init = Retry.__init__
        if not getattr(original_init, "_nexus_compat", False):
            def compatible_init(self, *args, **kwargs):
                if "method_whitelist" in kwargs and "allowed_methods" not in kwargs:
                    kwargs["allowed_methods"] = kwargs.pop("method_whitelist")
                return original_init(self, *args, **kwargs)

            compatible_init._nexus_compat = True
            Retry.__init__ = compatible_init
        return TrendReq(hl="pt-BR", tz=180, retries=2, backoff_factor=0.1, timeout=(10, 25))


def fetch_pytrends_fallback(limit: int = 10) -> list[str]:
    client = _trend_client()
    data = client.trending_searches(pn="brazil")
    if data is None or data.empty:
        raise RuntimeError("pytrends devolveu uma lista vazia.")
    return [str(item).strip() for item in data[0].tolist()[:limit] if str(item).strip()]


def _save_trends(values: list[str], source: str) -> None:
    clean = [str(value).strip() for value in values if str(value).strip()]
    st.session_state.real_trends = clean[:25]
    st.session_state.real_trends_source = source
    campaign_state.set_campaign(trends=clean[:25], source=source)


def _obter_trends() -> tuple[list[str], str]:
    errors: list[str] = []
    try:
        return fetch_google_trends_rss(), "Google Trending Now RSS — Brasil"
    except Exception as exc:
        errors.append(f"RSS: {exc}")
    try:
        return fetch_pytrends_fallback(), "pytrends — fallback"
    except Exception as exc:
        errors.append(f"pytrends: {exc}")
    st.session_state.trends_errors = errors
    return FALLBACK_TRENDS, "Radar de Contingência — sem dados em tempo real"


def obter_tendencias_reais(limit: int = 25) -> tuple[list[str], str]:
    """Busca e guarda tendências gerais para o radar avançado."""
    values, source = _obter_trends()
    values = values[:max(1, int(limit))]
    _save_trends(values, source)
    return values, source


def obter_tendencias_comerciais(limit: int = 12) -> tuple[list[str], str]:
    """Filtra o feed geral para sinais que podem virar consultas de produto."""
    values, source = obter_tendencias_reais(limit=25)
    commercial = filtrar_tendencias_comerciais(values, limit=limit)
    if not commercial:
        commercial = filtrar_tendencias_comerciais(FALLBACK_TRENDS, limit=limit)
        source = f"{source} · fallback comercial"
    _save_trends(commercial, f"{source} · filtro comercial")
    return commercial, f"{source} · filtro comercial"


def exibir_trends():
    st.header("📈 Google Trends Brasil: Inteligência em Tempo Real")
    st.markdown("Extraindo sinais recentes de procura para alimentar palavras-chave e ganchos da campanha.")
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔍 VARRER TENDÊNCIAS AGORA", use_container_width=True, type="primary"):
            with st.spinner("Consultando Google Trending Now Brasil..."):
                trends, source = obter_tendencias_reais()
                if source.startswith("Google Trending Now"):
                    st.success(f"✅ {len(trends)} tendências atuais capturadas pelo RSS oficial.")
                elif source.startswith("pytrends"):
                    st.warning("RSS indisponível; tendências obtidas pelo fallback pytrends.")
                else:
                    st.warning("Fonte em tempo real indisponível; usando Radar de Contingência.")

        if st.session_state.get("real_trends"):
            st.caption(f"Fonte: {st.session_state.get('real_trends_source', 'não identificada')}")
            termo_escolhido = st.selectbox("Selecione o alvo para o funil:", st.session_state.real_trends)
            if st.button("🚀 INJETAR NO MOTOR NEXUS", use_container_width=True):
                nome_limpo = termo_escolhido.title()
                campaign_state.set_campaign(
                    product_name=nome_limpo,
                    pain=f"Tendência recente detectada: {termo_escolhido}",
                    marketplace=st.session_state.get("mkt_global", "Mercado Livre"),
                    trend_term=termo_escolhido,
                    keywords=[termo_escolhido],
                    source=st.session_state.get("real_trends_source", "google_trends"),
                )
                st.success(f"'{nome_limpo}' injetado na campanha. Associe o produto e o link oficial antes de publicar.")
                time.sleep(0.5)
                st.rerun()
    with col2:
        st.subheader("💡 Por que usar Trends?")
        st.markdown("""
        1. **Demanda recente:** identifica assuntos com aumento de procura.
        2. **Ganchos:** os termos alimentam copy e legendas, não links inventados.
        3. **Validação:** tendência de busca não é garantia de compra; confirme o produto no marketplace.
        """)
        st.link_button("🌐 Abrir Google Trending Now Brasil", "https://trends.google.com/trending?geo=BR")
