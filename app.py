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

# --- FUNÇÃO DE CARD ESTILO V101 (RESTAURADA) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # Tratamento do Link de Afiliado
    link_final = link
    if "shopee" in link.lower():
        # Remove lixo do link e injeta seu ID
        base_link = link.split('?')[0]
        link_final = f"{base_link}?smtt=0.0.{ID_AFILIADO}"
    elif link == "#" or not link.startswith("http"):
        link_final = f"https://shopee.com.br/search?keyword={nome.replace(' ', '+')}"

    with st.container(border=True):
        st.markdown(f"### {ico} {nome}")
        
        col_data, col_stats = st.columns([2, 1])
        with col_data:
            st.markdown(f"💰 **Preço:** {valor}")
            st.markdown(f"🏷️ **Ticket:** {ticket}")
            st.link_button(f"🔗 VER NA {mkt_alvo.upper()}", link_final, use_container_width=True)
            
        with col_stats:
            st.metric("🔥 CALOR", f"{calor}°C")
            if st.button("🎯 SELECIONAR", key=f"sel_{idx}", use_container_width=True):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link_final
                st.success("✅ PRODUTO NO ARSENAL!")
                st.rerun()

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Login</h1>", unsafe_allow_html=True)
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("ACESSAR SISTEMA", use_container_width=True):
        if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# --- INICIALIZAÇÃO ---
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-pro')
if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- SIDEBAR CONTROL ---
st.sidebar.title("🔱 Nexus Control")
mkt = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt
ticket_filtro = st.sidebar.multiselect("Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])

# ABAS
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (MINERAÇÃO V101) ---
with tabs[0]:
    st.header(f"🔍 Minerador: {mkt}")
    
    # Quantidade de produtos definida por você
    qtd_miny = st.slider("Produtos para buscar:", 5, 20, 10)
    
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True):
        with st.spinner(f"Nexus vasculhando {mkt}..."):
            # Prompt que a IA entende perfeitamente
            prompt_scanner = f"""
            Aja como um minerador de tendências. Liste {qtd_miny} produtos virais da {mkt}.
            Filtro de ticket: {ticket_filtro}.
            Formato obrigatório: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url]
            Separe cada produto por ###
            """
            
            resultado = miny.minerar_produtos(prompt_scanner, mkt, st.session_state.motor_ia_obj)
            
            if resultado:
                # Limpa e fatias os blocos
                st.session_state.lista_produtos = [p.strip() for p in resultado.split("###") if "NOME:" in p.upper()]
                st.rerun()

    # Listagem em Grid (2 colunas para ficar igual ao seu print)
    if st.session_state.lista_produtos:
        cols = st.columns(2)
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # Fatiador de Dados
                dados = {}
                for item in bloco.split("|"):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        dados[k.strip().upper()] = v.strip()
                
                # Renderiza no Grid
                with cols[i % 2]:
                    renderizar_card_produto(
                        i,
                        dados.get("NOME", "Produto"),
                        dados.get("VALOR", "R$ 0,00"),
                        dados.get("CALOR", "50"),
                        dados.get("TICKET", "Médio"),
                        dados.get("LINK", "#"),
                        mkt
                    )
            except: continue

# --- CONEXÃO DAS ABAS ---
with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
with tabs[3]: studio_tab.exibir_estudio(miny, st.session_state.motor_ia_obj)
with tabs[4]: postador.exibir_postador()
with tabs[5]: update.dashboard_performance_simples()
