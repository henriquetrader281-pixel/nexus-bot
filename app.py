import streamlit as st
import arsenal 
import trends # <--- Linha 3: Garantir que não há espaços antes
import estudio
import pandas as pd
import update
import radar_engine 
import os
import urllib.parse
from datetime import datetime
import mineracao as miny # <--- Linha 11: Se der erro, apague o espaço antes do 'import'

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"**{ico} {nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        
        with c2:
            try:
                calor_num = min(max(int(calor), 0), 100)
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", width='stretch'):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.toast(f"Alvo Selecionado: {nome}")

# --- 3. SISTEMA DE ACESSO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Acesso:", type="password")
        if st.button("AUTENTICAR", width='stretch'):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado:
    login()

# --- 4. ESTADO DA SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox(
    "Marketplace Ativo:", 
    ["Shopee", "Mercado Livre", "Amazon"], 
    index=["Shopee", "Mercado Livre", "Amazon"].index(st.session_state.mkt_global)
)

motor_ia = st.sidebar.selectbox("Cérebro de IA:", ["gpt-4o-mini", "gemini-1.5-pro"])

# --- ALTERAÇÃO LINHA 84: ADICIONADA ABA TRENDS E REORDENADO ---
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Volume de Mineração:", [15, 30, 45], index=1)
    
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho da Operação:", value="Cozinha Criativa", key="nicho_input")

    if st.button(f"🔥 INICIAR VARREDURA {st.session_state.mkt_global.upper()}", width='stretch'):
        with st.spinner(f"Nexus minerando produtos virais em '{foco_nicho}'..."):
            # AJUSTE PARA O CACHE: Passamos as variáveis direto para a função bater com o cache
            resultado = miny.minerar_produtos(foco_nicho, st.session_state.mkt_global, motor_ia, qtd_produtos)
            st.session_state.res_busca = resultado
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha
