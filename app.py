import streamlit as st
import os
import autonomo_engine
import leads_engine
import global_engine
import scheduler_engine
import seo_engine
import update
import estudio
import backtest_engine
import postador

st.set_page_config(
    page_title="Nexus Master - Ecossistema de Vendas",
    page_icon="🔱",
    layout="wide"
)

# --- AUTENTICAÇÃO ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("NEXUS_PASSWORD", "admin"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔑 Insira a Chave de Acesso Nexus:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔑 Insira a Chave de Acesso Nexus:", type="password", on_change=password_entered, key="password")
        st.error("😕 Senha incorreta")
        return False
    else:
        return True

if not check_password():
    st.stop()

st.title("🔱 Nexus Master - Ecossistema de Vendas (Estrategista-Chefe)")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔱 Painel Nexus")
    mkt = st.selectbox("Marketplace Alvo:", ["Mercado Livre", "Shopee", "Amazon"], key="mkt_global_select")
    st.session_state.mkt_global = mkt
    st.divider()
    if st.button("♻️ Resetar Sessão", key="btn_reset_sidebar"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE DE ABAS ---
tabs = st.tabs([
    "🚀 AGENTE (1-CLIQUE)", 
    "📊 BACKTEST",
    "🎯 SNIPER DE LEADS", 
    "🌍 ESPIONAGEM GLOBAL",
    "⏰ AGENDADOR",
    "🔍 SEO & UBERSUGGEST",
    "🔍 SCANNER", 
    "🚀 ARSENAL", 
    "📈 TRENDS", 
    "🌍 RADAR", 
    "🎥 ESTÚDIO", 
    "🚀 CENTRAL DE DISPARO",
    "📊 DASHBOARD"
])

with tabs[0]:
    autonomo_engine.exibir_aba_autonomo()

with tabs[1]:
    backtest_engine.exibir_painel_backtest()

with tabs[2]:
    leads_engine.exibir_aba_leads()

with tabs[3]:
    global_engine.exibir_espionagem_global()

with tabs[4]:
    scheduler_engine.exibir_agendador()

with tabs[5]:
    seo_engine.exibir_seo_engine()

with tabs[6]: # SCANNER
    st.subheader("🔍 Scanner de Oportunidades Brutas")
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True, key="btn_start_scan"):
        st.success("Varredura concluída! Utilize a aba Agente para gerar o protocolo estratégico completo.")

with tabs[7]: # ARSENAL
    st.subheader("🚀 Arsenal de Copywriting & Gatilhos")
    st.markdown("Biblioteca de templates de alta conversão para o ecossistema Mercado Livre.")

with tabs[8]: # TRENDS
    st.subheader("📈 Google Trends & Termos Quentes")
    st.markdown("Monitorização em tempo real das tendências de busca do Brasil.")

with tabs[9]: # RADAR
    st.subheader("🌍 Radar Internacional")
    st.markdown("Insights de produtos validados na gringa prontos para adaptação.")

with tabs[10]: # ESTÚDIO
    st.subheader("🎥 Estúdio de Criativos & Vídeos Virais")
    # estudio.py não usa realmente os parâmetros miny e motor_ia internamente, passamos None como placeholder
    estudio.exibir_estudio(None, None)

with tabs[11]: # CENTRAL DE DISPARO
    postador.exibir_postador()

with tabs[12]: # DASHBOARD
    update.exibir_dashboard()
    st.divider()
    import self_optimizer
    self_optimizer.exibir_painel_evolutivo()
