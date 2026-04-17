import streamlit as st
import pandas as pd
import os
import json
import google.generativeai as genai
from datetime import datetime
import mineracao as miny
import arsenal
import trends
import postador
import studio_tab
import update

# --- 1. CONFIGURAÇÃO DE ELITE & ID FIXO ---
ID_AFILIADO = "18316451024"
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (LAYOUT V101 ORIGINAL) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # Lógica de Link Blindado (Injeta o seu ID se for Shopee)
    link_final = str(link).strip()
    if "shopee" in link_final.lower():
        base_link = link_final.split('?')[0]
        link_final = f"{base_link}?smtt=0.0.{ID_AFILIADO}"
    elif not link_final.startswith("http"):
        # Se a IA não mandar link, cria uma busca automática para facilitar sua vida
        link_final = f"https://shopee.com.br/search?keyword={nome.replace(' ', '+')}"

    with st.container(border=True):
        st.markdown(f"### {ico} {nome}")
        
        col_data, col_stats = st.columns([2, 1])
        with col_data:
            st.markdown(f"💰 **Preço:** {valor}")
            st.markdown(f"🏷️ **Ticket:** {ticket}")
            # Botão que abre o link externo em nova aba
            st.link_button(f"🔗 VER NA {mkt_alvo.upper()}", link_final, use_container_width=True)
            
        with col_stats:
            # Métrica de Calor que você gosta
            st.metric("🔥 CALOR", f"{calor}°C")
            if st.button("🎯 SELECIONAR", key=f"sel_{idx}", use_container_width=True):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link_final
                st.success("✅ PRODUTO NO ARSENAL!")
                st.rerun()

# --- 3. AUTENTICAÇÃO ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Login</h1>", unsafe_allow_html=True)
    senha = st.text_input("Acesso:", type="password")
    if st.button("ACESSAR SISTEMA", use_container_width=True):
        if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# --- 4. INICIALIZAÇÃO DO CÉREBRO IA ---
if "motor_ia_obj" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')
    except: st.error("Erro no motor Gemini.")

if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- 5. SIDEBAR CONTROL ---
st.sidebar.title("🔱 Nexus Control")
mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt_global
filtro_ticket = st.sidebar.multiselect("Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])

# ABAS
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (LÓGICA RECUPERADA DAS VERSÕES QUE FUNCIONAVAM) ---
with tabs[0]:
    st.header(f"🔍 Minerador: {mkt_global}")
    qtd_miny = st.slider("Quantidade de achados:", 5, 20, 10)
    
    if st.button("🚀 INICIAR VARREDURA DE ELITE", use_container_width=True):
        with st.spinner(f"Nexus minerando {mkt_global}..."):
            # Prompt reforçado que força o fatiamento correto
            prompt_scanner = f"""
            Aja como um minerador de tendências. Liste {qtd_miny} produtos virais da {mkt_global}.
            Filtro de ticket: {filtro_ticket}.
            Retorne EXATAMENTE neste formato para cada item:
            NOME: [nome] | VALOR: [preço] | CALOR: [numero 0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url]
            Separe cada produto pelo marcador: ###
            """
            
            # Chama o mineracao.py que usa o Llama 3.3 (Groq)
            resultado = miny.minerar_produtos(prompt_scanner, mkt_global, st.session_state.motor_ia_obj)
            
            if resultado:
                # O segredo das versões antigas: limpeza de markdown e fatiamento por ###
                texto_limpo = resultado.replace("**", "").replace("`", "")
                st.session_state.lista_produtos = [p.strip() for p in texto_limpo.split("###") if "NOME:" in p.upper()]
                st.rerun()

    # Exibição em Grid de 2 Colunas (Igual ao seu print de sucesso)
    if st.session_state.lista_produtos:
        grid = st.columns(2)
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # Fatiador Universal: Pega o que está entre os "|"
                dados = {}
                for item in bloco.split("|"):
                    if ":" in item:
                        chave, valor = item.split(":", 1)
                        dados[chave.strip().upper()] = valor.strip()
                
                # Renderiza no Grid
                with grid[i % 2]:
                    renderizar_card_produto(
                        i,
                        dados.get("NOME", "Produto"),
                        dados.get("VALOR", "Consultar"),
                        dados.get("CALOR", "50"),
                        dados.get("TICKET", "Médio"),
                        dados.get("LINK", "#"),
                        mkt_global
                    )
            except: continue

# --- CONEXÃO COM AS OUTRAS ABAS ---
with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
with tabs[3]: studio_tab.exibir_estudio(miny, st.session_state.motor_ia_obj)
with tabs[4]: postador.exibir_postador()
with tabs[5]: update.dashboard_performance_simples()
