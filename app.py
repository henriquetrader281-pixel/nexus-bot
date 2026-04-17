import streamlit as st
import pandas as pd
import os
import json
import google.generativeai as genai
from datetime import datetime

# --- IMPORTAÇÃO DE MÓDULOS ---
import mineracao as miny
import arsenal
import trends
import postador
import studio_tab
import update

# --- CONFIGURAÇÃO E ID FIXO ---
ID_AFILIADO = "18316451024"
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- FUNÇÃO DE CARD (COM LINK EXTERNO REAL) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # Injeta o ID de afiliado se for Shopee
    link_final = link
    if "shopee" in link.lower() and ID_AFILIADO not in link:
        link_final = f"{link}?smtt=0.0.{ID_AFILIADO}"

    with st.container(border=True):
        col_info, col_stats, col_btn = st.columns([3, 1.5, 1])
        with col_info:
            st.markdown(f"**{ico} {nome}**")
            st.markdown(f"🔗 [ABRIR NA {mkt_alvo.upper()}]({link_final})")
        with col_stats:
            st.markdown(f"💰 **{valor}**")
            st.markdown(f"🏷️ Ticket: **{ticket}**")
        with col_btn:
            st.metric("🔥 Calor", f"{calor}°C")
            if st.button("🎯 Selecionar", key=f"btn_{idx}", use_container_width=True):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link_final
                st.success("📦 Capturado!")
                st.rerun()

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Login</h1>", unsafe_allow_html=True)
    senha = st.text_input("Senha:", type="password")
    if st.button("ENTRAR"):
        if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# --- INICIALIZAÇÃO ---
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-pro')
if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- INTERFACE ---
st.sidebar.title("🔱 Nexus Control")
mkt = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt
ticket_filtro = st.sidebar.multiselect("Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (O CORAÇÃO) ---
with tabs[0]:
    st.header(f"🔍 Minerador de Elite: {mkt}")
    qtd = st.slider("Quantidade de produtos:", 5, 20, 10)
    
    if st.button("🚀 INICIAR MINERAÇÃO AGORA", use_container_width=True):
        with st.spinner(f"Nexus vasculhando {mkt}..."):
            # Prompt de altíssima precisão
            prompt_scanner = f"""
            Aja como um especialista em produtos virais. Busque {qtd} produtos tendência na {mkt} com ticket {ticket_filtro}.
            Retorne os dados EXATAMENTE assim para cada produto, sem exceção:
            NOME: [nome do produto] | VALOR: [R$ preço] | CALOR: [numero de 0 a 100] | TICKET: [Baixo/Médio/Alto] | LINK: [url real]
            ###
            """
            # Chama o mineracao.py
            resultado = miny.minerar_produtos(prompt_scanner, mkt, st.session_state.motor_ia_obj)
            
            if resultado:
                # Divide pela marcação ### e remove lixo
                st.session_state.lista_produtos = [p.strip() for p in resultado.split("###") if "NOME:" in p.upper()]
                st.success(f"✅ {len(st.session_state.lista_produtos)} Produtos Minerados!")
                st.rerun()

    # Exibição dos cards
    if st.session_state.lista_produtos:
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # Fatiador que não quebra
                temp = {}
                for item in bloco.split("|"):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        temp[k.strip().upper()] = v.strip()
                
                renderizar_card_produto(
                    i, 
                    temp.get("NOME", "Produto"), 
                    temp.get("VALOR", "R$ 0,00"), 
                    temp.get("CALOR", "50"), 
                    temp.get("TICKET", "Médio"), 
                    temp.get("LINK", "#"), 
                    mkt
                )
            except: continue

# --- CONEXÃO COM OS OUTROS ARQUIVOS ---
with tabs[1]: 
    if "sel_nome" in st.session_state:
        arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
    else: st.info("Selecione um produto no Scanner.")

with tabs[2]: trends.exibir_trends()
with tabs[3]: studio_tab.exibir_estudio(miny, st.session_state.motor_ia_obj)
with tabs[4]: postador.exibir_postador()
with tabs[5]: update.dashboard_performance_simples()
