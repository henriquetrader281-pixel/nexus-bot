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

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- 2. LAYOUT DOS CARDS (CORREÇÃO DE LINK E DESIGN) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # Validação de Link: Se não começar com http, tratamos como busca
    link_real = link if link.startswith("http") else f"https://www.google.com/search?q={mkt_alvo}+{nome}"

    with st.container(border=True):
        col_info, col_stats, col_btn = st.columns([3, 1.5, 1])
        
        with col_info:
            st.markdown(f"**{ico} {nome}**")
            # CORREÇÃO GRAVE: Link externo real
            st.write(f"🔗 [Ir para {mkt_alvo}]({link_real})")
            
        with col_stats:
            st.markdown(f"💰 **{valor}**")
            st.markdown(f"🏷️ Ticket: **{ticket}**")
            
        with col_btn:
            c_val = "".join(filter(str.isdigit, str(calor))) or "50"
            st.metric("🔥 Calor", f"{c_val}°C")
            if st.button("🎯 Selecionar", key=f"btn_{idx}", use_container_width=True):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link_real
                st.success("✅ Produto Capturado!")
                st.rerun()

# --- 3. LOGIN E SEGURANÇA ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Acesso:", type="password")
        if st.button("LOGAR", use_container_width=True):
            if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Incorreto.")
    st.stop()

# --- 4. ESTADOS E MOTOR ---
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-pro')

if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- 5. SIDEBAR (CONTROLE) ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
ticket_selecionado = st.sidebar.multiselect("Filtrar Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])

# --- 6. ABAS NAVEGAÇÃO ---
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner {st.session_state.mkt_global}")
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        qtd = st.selectbox("Volume:", [5, 10, 15, 20])
    with col_cfg2:
        st.info(f"Filtro: {', '.join(ticket_selecionado)}")

    if st.button("🚀 INICIAR VARREDURA DE ELITE", use_container_width=True):
        with st.spinner("Minerando oportunidades..."):
            # Prompt reforçado com a seleção de Ticket
            prompt_scanner = f"""
            Liste {qtd} produtos virais da {st.session_state.mkt_global} com ticket {ticket_selecionado}.
            Formato OBRIGATÓRIO: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url real do produto] ###
            """
            resultado_raw = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, st.session_state.motor_ia_obj)
            
            if resultado_raw:
                st.session_state.lista_produtos = [p.strip() for p in resultado_raw.split("###") if len(p) > 20]
                st.rerun()

    if st.session_state.lista_produtos:
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # Fatiador Elite: Captura links e tickets sem erro
                d = {}
                for part in bloco.split("|"):
                    if ":" in part:
                        chave, valor = part.split(":", 1)
                        d[chave.strip().upper()] = valor.strip()
                
                renderizar_card_produto(
                    i, 
                    d.get("NOME", "Produto"), 
                    d.get("VALOR", "Sob consulta"), 
                    d.get("CALOR", "50"), 
                    d.get("TICKET", "Médio"), 
                    d.get("LINK", "#"), 
                    st.session_state.mkt_global
                )
            except: continue

# --- CONEXÃO DAS OUTRAS ABAS ---
with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
with tabs[3]: studio_tab.exibir_estudio(miny, st.session_state.motor_ia_obj)
with tabs[4]: postador.exibir_postador()
with tabs[5]: update.dashboard_performance_simples()
