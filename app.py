from __future__ import annotations

import streamlit as st
import os


def get_secret(name: str, default=None):
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value if value not in (None, "") else os.environ.get(name, default)


import autonomo_engine
import campaign_state
import creator_hub
import descoberta_hub
import inteligencia_hub
import ml_afiliados_engine
import postador
import simple_mode
import scheduler_engine
import seo_engine
import update
import backtest_engine


st.set_page_config(
    page_title="Nexus Master - Ecossistema de Vendas",
    page_icon="🔱",
    layout="wide",
)


def check_password() -> bool:
    def password_entered() -> None:
        if st.session_state["password"] == get_secret("NEXUS_PASSWORD", "admin"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔑 Insira a Chave de Acesso Nexus:", type="password", on_change=password_entered, key="password")
        return False
    if not st.session_state["password_correct"]:
        st.text_input("🔑 Insira a Chave de Acesso Nexus:", type="password", on_change=password_entered, key="password")
        st.error("Senha incorreta")
        return False
    return True


if not check_password():
    st.stop()

st.title("🔱 Nexus Master - Ecossistema de Vendas")

with st.sidebar:
    st.title("🔱 Painel Nexus")
    marketplace = st.selectbox(
        "Marketplace alvo",
        ["Mercado Livre", "Shopee", "Amazon"],
        key="mkt_global_select",
    )
    st.session_state.mkt_global = marketplace
    st.divider()
    campaign = campaign_state.get_campaign()
    if campaign.get("product_name"):
        st.success(f"Campanha ativa: {campaign['product_name']}")
        st.caption(campaign.get("official_affiliate_url") or "Link oficial ainda não associado")
    else:
        st.info("Nenhuma campanha ativa")
    if st.button("♻️ Limpar campanha", key="btn_reset_sidebar"):
        campaign_state.clear_campaign()
        st.rerun()


tabs = st.tabs([
    "🚀 MODO SIMPLES",
    "🧠 AVANÇADO",
    "📊 BACKTEST",
    "🎯 INTELIGÊNCIA & LEADS",
    "⏰ AGENDADOR",
    "🔍 SEO",
    "🔎 DESCOBERTA",
    "🎬 STUDIO & COPY",
    "🚀 CENTRAL DE DISPARO",
    "🤝 AFILIADOS",
    "📊 DASHBOARD",
])

with tabs[0]:
    simple_mode.exibir_modo_simples()

with tabs[1]:
    autonomo_engine.exibir_aba_autonomo()

with tabs[2]:
    backtest_engine.exibir_painel_backtest()

with tabs[3]:
    inteligencia_hub.exibir_inteligencia_leads()

with tabs[4]:
    scheduler_engine.exibir_agendador()

with tabs[5]:
    seo_engine.exibir_seo_engine()

with tabs[6]:
    descoberta_hub.exibir_descoberta()

with tabs[7]:
    creator_hub.exibir_creator_hub()

with tabs[8]:
    postador.exibir_postador()

with tabs[9]:
    ml_afiliados_engine.exibir_config_ml()

with tabs[10]:
    update.exibir_dashboard()
    st.divider()
    import self_optimizer
    self_optimizer.exibir_painel_evolutivo()
