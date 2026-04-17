import streamlit as st
import pandas as pd
import os
import json
import google.generativeai as genai
from datetime import datetime

# --- IMPORTAÇÃO DE MÓDULOS NEXUS ---
import mineracao as miny
import arsenal
import trends
import postador
import studio_tab
import update

# --- 1. CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- 2. MOTOR DE INTELIGÊNCIA (GEMINI) ---
def get_nexus_intelligence():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-pro')
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"Analise tendências virais de HOJE ({hoje}) no TikTok Brasil e Instagram Reels. Retorne APENAS um JSON com chaves: musica, razao, aida_hook, score."
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except:
        return {"trends": []}

# --- 3. LAYOUT DOS CARDS (SISTEMA DE COLUNAS) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        col_info, col_stats, col_btn = st.columns([3, 1.5, 1])
        
        with col_info:
            st.markdown(f"**{ico} {nome}**")
            st.caption(f"🔗 [Link do Produto]({link})")
            
        with col_stats:
            st.markdown(f"💰 **{valor}**")
            st.markdown(f"🏷️ Ticket: **{ticket}**")
            
        with col_btn:
            # Limpa o calor para garantir que seja apenas número para o gráfico/métrica
            c_val = "".join(filter(str.isdigit, str(calor))) or "50"
            st.metric("🔥 Calor", f"{c_val}°C")
            if st.button("🎯 Selecionar", key=f"btn_{idx}", use_container_width=True):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link
                st.success("✅ Enviado!")
                st.rerun()

# --- 4. SEGURANÇA E LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Senha de Elite:", type="password")
        if st.button("AUTENTICAR", use_container_width=True):
            if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Acesso negado.")
    st.stop()

# --- 5. INICIALIZAÇÃO DE ESTADOS ---
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-pro')

if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- 6. INTERFACE LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/11186/11186523.png", width=100)
st.sidebar.title("Nexus Control")
mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt_global

# --- 7. NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (O MOTOR DE BUSCA) ---
with tabs[0]:
    st.header(f"🔍 Scanner {mkt_global}")
    qtd = st.selectbox("Volume de Mineração:", [5, 10, 15, 20])
    
    if st.button("🚀 INICIAR VARREDURA DE ELITE", use_container_width=True):
        with st.spinner("Buscando Oportunidades..."):
            # Prompt Blindado
            prompt_scanner = f"Liste {qtd} produtos virais da {mkt_global}. Use EXATAMENTE o formato: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url] ###"
            resultado_raw = miny.minerar_produtos(prompt_scanner, mkt_global, st.session_state.motor_ia_obj)
            
            if resultado_raw:
                st.session_state.lista_produtos = [p.strip() for p in resultado_raw.split("###") if len(p) > 20]
                st.rerun()

    if st.session_state.lista_produtos:
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # Fatiador Universal Nexus
                d = {k.split(":")[0].strip().upper(): k.split(":")[1].strip() for k in bloco.split("|") if ":" in k}
                renderizar_card_produto(
                    i, 
                    d.get("NOME", "Produto"), 
                    d.get("VALOR", "Sob consulta"), 
                    d.get("CALOR", "50"), 
                    d.get("TICKET", "Médio"), 
                    d.get("LINK", "#"), 
                    mkt_global
                )
            except: continue

# --- ABA 1: ARSENAL ---
with tabs[1]:
    arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)

# --- ABA 2: TRENDS ---
with tabs[2]:
    trends.exibir_trends()

# --- ABA 3: ESTÚDIO (VEO 3 PROMPT) ---
with tabs[3]:
    studio_tab.exibir_estudio(miny, st.session_state.motor_ia_obj)

# --- ABA 4: POSTADOR ---
with tabs[4]:
    postador.exibir_postador()

# --- ABA 5: DASHBOARD ---
with tabs[5]:
    update.dashboard_performance_simples()
