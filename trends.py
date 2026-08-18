from __future__ import annotations

import time
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


def exibir_trends():
    st.header("📈 Google Trends Brasil: Inteligência em Tempo Real")
    st.markdown("Extraindo sinais recentes de procura para alimentar palavras-chave e ganchos da campanha.")
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔍 VARRER TENDÊNCIAS AGORA", use_container_width=True, type="primary"):
            with st.spinner("Consultando Google Trending Now Brasil..."):
                trends, source = _obter_trends()
                _save_trends(trends, source)
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
