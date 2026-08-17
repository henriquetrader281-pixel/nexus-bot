from __future__ import annotations

import time

import pandas as pd
import streamlit as st
from pytrends.request import TrendReq

import campaign_state


def _trend_client() -> TrendReq:
    """Cria o cliente pytrends com compatibilidade urllib3 1.x/2.x."""
    try:
        return TrendReq(hl="pt-BR", tz=180, retries=2, backoff_factor=0.1, timeout=(10, 25))
    except TypeError as exc:
        if "method_whitelist" not in str(exc):
            raise
        # pytrends 4.9.2 ainda envia method_whitelist, removido no urllib3 2.x.
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


def _save_trends(values: list[str], source: str) -> None:
    clean = [str(value).strip() for value in values if str(value).strip()]
    st.session_state.real_trends = clean[:10]
    campaign_state.set_campaign(trends=clean[:10], source=source)


def exibir_trends():
    st.header("📈 Google Trends Brasil: Inteligência em Tempo Real")
    st.markdown("Extraindo as dores e desejos mais quentes do mercado brasileiro agora.")
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔍 VARRER TENDÊNCIAS AGORA", use_container_width=True, type="primary"):
            with st.spinner("Conectando aos servidores do Google Trends..."):
                try:
                    pytrends = _trend_client()
                    df = pytrends.trending_searches(pn="brazil")
                    if df is None or df.empty:
                        raise RuntimeError("Google retornou lista vazia.")
                    _save_trends(df[0].tolist(), "google_trends")
                    st.success("✅ Tendências capturadas com sucesso!")
                except Exception as exc:
                    st.error(f"⚠️ Limite de requisições ou erro de conexão: {exc}")
                    st.info("Usando Radar de Contingência (Termos quentes validados):")
                    fallback_trends = [
                        "Organizador de Cozinha Inteligente",
                        "Luminária LED Monitor Anti-Reflexo",
                        "Mini Pistola de Massagem Profissional",
                        "Mop Giratório Slim 2026",
                        "Fone Bluetooth Cancelamento Ruído",
                    ]
                    _save_trends(fallback_trends, "google_trends_fallback")

        if st.session_state.get("real_trends"):
            termo_escolhido = st.selectbox("Selecione o alvo para o funil:", st.session_state.real_trends)
            if st.button("🚀 INJETAR NO MOTOR NEXUS", use_container_width=True):
                nome_limpo = termo_escolhido.title()
                campaign_state.set_campaign(
                    product_name=nome_limpo,
                    pain=f"Tendência em alta detectada: {termo_escolhido}",
                    marketplace=st.session_state.get("mkt_global", "Mercado Livre"),
                    trend_term=termo_escolhido,
                    source="google_trends",
                )
                st.success(f"'{nome_limpo}' injetado na campanha. Agora associe o link oficial do produto no Scanner ou no Agente.")
                time.sleep(1)
                st.rerun()
    with col2:
        st.subheader("💡 Por que usar Trends?")
        st.markdown("""
        1. **Demanda Validada:** Você só vende o que as pessoas já estão procurando.
        2. **SEO Nativo:** O Nexus usa estes termos exatos para que o seu post apareça no topo das buscas.
        3. **ROI Elevado:** Menor custo por clique em anúncios.
        """)
        st.link_button("🌐 Abrir Google Trends", "https://trends.google.com.br/trends/")
