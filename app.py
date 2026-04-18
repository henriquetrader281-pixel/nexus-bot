import streamlit as st
import arsenal
import trends
import pandas as pd
import update
import os
import urllib.parse
from datetime import datetime
import mineracao as miny
import estudio
import google.generativeai as genai
import json
import radar_engine

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- LOGIN E ESTADOS ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Acesso:", type="password", key="login_pass")
        if st.button("AUTENTICAR", use_container_width=True, key="btn_login"):
            if senha == st.secrets["NEXUS_PASSWORD"]:
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

# --- INICIALIZAÇÃO BLINDADA DO GEMINI ---
def inicializar_motor_ia():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Forçando o 1.5-pro para o seu plano PLUS
        return genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        st.error(f"Erro ao conectar com Gemini Pro: {e}")
        return None

# Garante que a IA seja carregada apenas uma vez
if "motor_ia_obj" not in st.session_state:
    st.session_state.motor_ia_obj = inicializar_motor_ia()

# --- SIDEBAR FIXA (Resolve o DuplicateElementId) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/trident.png", width=80)
    st.title("Nexus Control")
    
    # Marketplace com KEY única para não bugar o Scanner
    mkt = st.selectbox(
        "Marketplace:", 
        ["Shopee", "Amazon", "Mercado Livre"], 
        key="selectbox_mkt_principal"
    )
    st.session_state.mkt_global = mkt
    
    st.divider()
    # Botão de Reset com KEY única
    if st.button("♻️ Resetar Conexão IA", key="btn_reset_ia_final"):
        st.session_state.motor_ia_obj = inicializar_motor_ia()
        st.toast("Conexão com Gemini Pro Restaurada!")
        st.rerun()

# --- INTERFACE DE ABAS ---
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

with tabs[0]: # SCANNER
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True, key="btn_scan_nexus"):
        with st.spinner(f"Minerando {mkt}..."):
            prompt = f"Liste 10 produtos virais da {mkt}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt, mkt, "groq")

    if st.session_state.get("res_busca"):
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            if "|" in linha:
                try:
                    partes = linha.replace("**", "").split("|")
                    d = {p.split(":", 1)[0].strip().upper(): p.split(":", 1)[1].strip() for p in partes if ":" in p}
                    renderizar_card_produto(idx, d.get("NOME"), d.get("VALOR"), d.get("CALOR"), d.get("TICKET"), d.get("URL"), mkt)
                except: continue

with tabs[1]: # ARSENAL
    if st.session_state.motor_ia_obj:
        arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
    else:
        st.warning("⚠️ IA Desconectada. Clique em 'Resetar' na barra lateral.")

with tabs[2]: # TRENDS
    trends.exibir_trends()

with tabs[3]: # RADAR
    radar_engine.exibir_radar()

with tabs[4]: # ESTÚDIO
    st.info("🎥 Módulo de Produção de Criativos.")

with tabs[5]: # DASHBOARD
    st.info("📊 Performance e Cliques.")
