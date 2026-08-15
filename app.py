import streamlit as st
import os
import autonomo_engine
import leads_engine
import global_engine
import scheduler_engine
import seo_engine
import update
import studio_tab
import backtest_engine
import postador
import ml_afiliados_engine
import arsenal
import trends
import radar_engine
import mineracao
import google.generativeai as genai # Placeholder para motor_ia

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
    "🤝 AFILIADOS ML",
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
    st.markdown("Varredura profunda nos marketplaces para identificar produtos com alta demanda e baixa concorrência.")
    
    c_scan1, c_scan2 = st.columns([1, 1])
    with c_scan1:
        nicho_scan = st.text_input("Nicho para Varredura:", value="Cozinha Inteligente")
    with c_scan2:
        mkt_scan = st.selectbox("Marketplace Alvo:", ["Mercado Livre", "Shopee", "Amazon"], key="mkt_scan_select")

    if st.button("🚀 INICIAR VARREDURA PROFUNDA", use_container_width=True, key="btn_start_scan"):
        with st.spinner(f"Escaneando {mkt_scan} para o nicho {nicho_scan}..."):
            prompt_scan = f"Liste 5 produtos virais e promissores de {nicho_scan} no {mkt_scan} com alto potencial de venda."
            res_scan = mineracao.minerar_produtos(prompt_scan, mkt_scan, None)
            st.session_state.scan_results = res_scan
            st.success("Varredura concluída!")

    if "scan_results" in st.session_state:
        st.divider()
        st.markdown("#### 📦 Produtos Detectados:")
        linhas = st.session_state.scan_results.split('\n')
        for linha in linhas:
            if "|" in linha:
                with st.container(border=True):
                    st.write(linha)
                    nome_prod = linha.split('|')[0].replace("NOME:", "").strip()
                    if st.button(f"🎯 ATIVAR {nome_prod.upper()}", key=f"act_{nome_prod}"):
                        st.session_state.sel_nome = nome_prod
                        st.session_state.sel_dor = f"Produto detectado no Scanner: {nicho_scan}"
                        st.success(f"'{nome_prod}' ativado! Vá à aba Agente ou Arsenal.")
                        st.rerun()

with tabs[7]: # ARSENAL
    # Inicializa motor_ia como None ou mock se necessário
    arsenal.exibir_arsenal(mineracao, None)

with tabs[8]: # TRENDS
    trends.exibir_trends()

with tabs[9]: # RADAR
    radar_engine.exibir_radar()

with tabs[10]: # ESTÚDIO
    studio_tab.exibir_estudio(mineracao, None)

with tabs[11]: # CENTRAL DE DISPARO
    postador.exibir_postador()

with tabs[12]: # AFILIADOS ML
    ml_afiliados_engine.exibir_config_ml()

with tabs[13]: # DASHBOARD
    update.exibir_dashboard()
    st.divider()
    import self_optimizer
    self_optimizer.exibir_painel_evolutivo()
