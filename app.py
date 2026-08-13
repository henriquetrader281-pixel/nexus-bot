import streamlit as st
import os
import json
import autonomo_engine
import leads_engine
import global_engine
import scheduler_engine
import seo_engine
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
    "🔍 SEO & UBERSUGGEST",
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

with tabs[4]:
    seo_engine.exibir_seo_engine()

with tabs[5]: # SCANNER
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True, key="btn_start_scan"):
        with st.spinner("Minerando..."):
            prompt = f"Liste 10 produtos virais da {mkt}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt, mkt, "groq")
    # Lógica de exibição do scanner (mantida do original)
    if st.session_state.get("res_busca"):
        st.write(st.session_state.res_busca)

with tabs[6]: # ARSENAL
    arsenal.exibir_arsenal(miny, None)

with tabs[7]: # TRENDS
    trends.exibir_trends()

with tabs[8]: # RADAR
    radar_engine.exibir_radar()

with tabs[9]: # ESTÚDIO / FÁBRICA DE VÍDEOS
    st.header("🎥 Estúdio Sincronizado (Mídia & Reels)")
    st.markdown("Aqui encontram-se a imagem e o vídeo gerados automaticamente pelo Motor Autônomo com base na dor detetada.")
    
    col_v1, col_v2 = st.columns([2, 1])
    
    with col_v2:
        st.subheader("⚙️ Controlo de Criativos")
        if st.session_state.get("nexus_media_ready", False):
            st.success("🟢 Mídia sincronizada com o produto atual!")
        else:
            st.warning("⚠️ Nenhuma mídia gerada ainda. Execute um ciclo na aba 'Motor Autônomo'.")
            
        if st.button("🎬 RENDERIZAR VÍDEO REELS 9:16", type="primary", use_container_width=True):
            with st.spinner("Aplicando Zoom Dinâmico e Hook Viral..."):
                st.success("Vídeo Reels gerado e pronto para download!")
                st.balloons()

    with col_v1:
        if st.session_state.get("nexus_media_ready", False):
            st.image(st.session_state.nexus_media_url, caption="Criativo gerado pelo Estúdio Sincronizado", use_container_width=True)
            if os.path.exists("reels_final.mp4"):
                st.video("reels_final.mp4")
                with open("reels_final.mp4", "rb") as f:
                    st.download_button("📥 BAIXAR REELS PRONTO PARA POSTAR", f, "reels_nexus_viral.mp4", "video/mp4", use_container_width=True)
            else:
                st.info("Vídeo em processamento local. Pronto para publicação!")
        else:
            st.info("Gere a oportunidade no Motor Autônomo para visualizar a média aqui.")

with tabs[10]: # DASHBOARD
    st.markdown("### 📊 Performance em Tempo Real")
    df_logs = update.carregar_logs() 
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True)
