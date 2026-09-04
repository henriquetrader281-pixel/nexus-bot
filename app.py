from __future__ import annotations

import importlib

import streamlit as st
from auth import check_password as password_matches, configured_password


import autonomo_engine
import campaign_state
import creator_hub
import descoberta_hub
import inteligencia_hub
import ml_afiliados_engine
import postador
import simple_mode
import nexus_pipeline_ui
import scheduler_engine
import seo_engine
import update
import backtest_engine
import health_check
from video_machine import studio_tab as video_machine_studio_tab
from video_machine import metrics_tab as video_machine_metrics_tab


st.set_page_config(
    page_title="Nexus Master - Ecossistema de Vendas",
    page_icon="🔱",
    layout="wide",
)


def check_password() -> bool:
    def password_entered() -> None:
        if password_matches(st.session_state["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        if configured_password() is None:
            st.error("NEXUS_PASSWORD não configurada. Defina esse segredo antes de iniciar o Nexus.")
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
    "🚀 ESTEIRA PRINCIPAL",
    "🎬 MÁQUINA DE VÍDEOS",
    "📈 MÉTRICAS",
    "📊 MONITOR DE MERCADO",
    "🧠 AVANÇADO",
])

with tabs[0]:
    nexus_pipeline_ui.exibir_esteira_principal()

with tabs[1]:
    video_machine_studio_tab.exibir_maquina_videos()

with tabs[2]:
    video_machine_metrics_tab.exibir_painel_metricas()

with tabs[3]:
    import monitor_app
    # O monitor é um módulo top-level; reload é necessário para que cada rerun
    # do st_autorefresh recarregue preço, candles e ponteiros no app integrado.
    importlib.reload(monitor_app)

with tabs[4]:
    st.header("🧠 Ferramentas avançadas")
    st.caption("A operação normal não precisa destas áreas. Use-as apenas para diagnóstico, SEO, backtest, agendamento e configurações específicas.")
    with st.expander("🩺 Diagnóstico de operação", expanded=True):
        health_check.render_panel(st)
    autonomo_engine.exibir_aba_autonomo()
    with st.expander("📊 Backtest e inteligência", expanded=False):
        backtest_engine.exibir_painel_backtest()
        inteligencia_hub.exibir_inteligencia_leads()
    with st.expander("⏰ Agendamento e descoberta", expanded=False):
        scheduler_engine.exibir_agendador()
        descoberta_hub.exibir_descoberta()
    with st.expander("🔍 SEO e Studio", expanded=False):
        seo_engine.exibir_seo_engine()
        creator_hub.exibir_creator_hub()
    with st.expander("🚀 Central de Disparo manual", expanded=False):
        postador.exibir_postador()
    with st.expander("🤝 Afiliados e Dashboard", expanded=False):
        ml_afiliados_engine.exibir_config_ml()
        update.exibir_dashboard()
        st.divider()
        import self_optimizer
        self_optimizer.exibir_painel_evolutivo()
