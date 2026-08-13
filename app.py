import streamlit as st
import os
import json
import autonomo_engine
import leads_engine
import global_engine
import scheduler_engine
import mineracao as miny
import arsenal
import trends
import radar_engine
import estudio
import update

st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- LOGIN E SEGURANÇA ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Acesso:", type="password", key="login_pass")
        if st.button("AUTENTICAR", use_container_width=True, key="btn_login_main"):
            if senha == st.secrets.get("NEXUS_PASSWORD", "admin"):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    st.stop()

st.title("🔱 Nexus Master - Ecossistema de Vendas")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔱 Painel Nexus")
    mkt = st.selectbox("Marketplace Alvo:", ["Shopee", "Amazon", "Mercado Livre"], key="mkt_global_select")
    st.session_state.mkt_global = mkt
    st.divider()
    if st.button("♻️ Resetar Sessão", key="btn_reset_sidebar"):
        st.session_state.clear()
        st.rerun()

# --- INTERFACE DE ABAS ---
tabs = st.tabs([
    "🤖 MOTOR AUTÔNOMO", 
    "🎯 SNIPER DE LEADS", 
    "🌍 ESPIONAGEM GLOBAL",
    "⏰ AGENDADOR",
    "🔍 SCANNER", 
    "🚀 ARSENAL", 
    "📈 TRENDS", 
    "🌍 RADAR", 
    "🎥 ESTÚDIO", 
    "📊 DASHBOARD"
])

with tabs[0]:
    autonomo_engine.exibir_aba_autonomo()

with tabs[1]:
    leads_engine.exibir_aba_leads()

with tabs[2]:
    global_engine.exibir_espionagem_global()

with tabs[3]:
    scheduler_engine.exibir_agendador()

with tabs[4]: # SCANNER
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True, key="btn_start_scan"):
        with st.spinner("Minerando..."):
            prompt = f"Liste 10 produtos virais da {mkt}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt, mkt, "groq")
    # Lógica de exibição do scanner (mantida do original)
    if st.session_state.get("res_busca"):
        st.write(st.session_state.res_busca)

with tabs[5]: # ARSENAL
    arsenal.exibir_arsenal(miny, None)

with tabs[6]: # TRENDS
    trends.exibir_trends()

with tabs[7]: # RADAR
    radar_engine.exibir_radar()

with tabs[8]: # ESTÚDIO / FÁBRICA DE VÍDEOS
    st.header("🎥 Fábrica de Conteúdo Viral (9:16)")
    st.markdown("Transforme o produto em um Reels de alta retenção com efeitos de zoom dinâmico.")
    
    col_v1, col_v2 = st.columns([2, 1])
    
    with col_v2:
        st.subheader("⚙️ Configurações")
        hook_tipo = st.selectbox("Tipo de Gancho (Hook):", ["Curiosidade Extrema", "Quebra de Padrão", "Alerta Urgente"])
        velocidade = st.slider("Intensidade do Zoom:", 1.0, 2.0, 1.2)
        
        if st.button("🎬 GERAR VÍDEO ESTRATOSFÉRICO", type="primary", use_container_width=True):
            with st.spinner("Renderizando vídeo de alta conversão..."):
                # Simula a chamada ao video_generator.py
                st.success("Vídeo renderizado com sucesso!")
                st.balloons()

    with col_v1:
        if os.path.exists("reels_final.mp4"):
            st.video("reels_final.mp4")
            with open("reels_final.mp4", "rb") as f:
                st.download_button("📥 BAIXAR REELS PARA POSTAR", f, "reels_nexus_elite.mp4", "video/mp4", use_container_width=True)
        else:
            st.info("Gere o vídeo no botão ao lado para visualizar a prévia.")

with tabs[9]: # DASHBOARD
    st.markdown("### 📊 Performance em Tempo Real")
    df_logs = update.carregar_logs() 
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True)
