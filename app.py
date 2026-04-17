import streamlit as st
import pandas as pd
import os
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

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (LAYOUT RAIZ) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # --- LIMPEZA DE LINK NINJA (CORREÇÃO DEFINITIVA) ---
    # Remove qualquer lixo visual que a IA coloque (colchetes, espaços, aspas)
    link_limpo = str(link).replace("]", "").replace("[", "").replace("(", "").replace(")", "").replace(" ", "").strip()
    link_base = link_limpo.split('?')[0]
    
    if "shopee" in link_base.lower():
        link_final = f"{link_base}?smtt=0.0.{ID_AFILIADO}"
    else:
        link_final = link_base if link_base.startswith("http") else f"https://shopee.com.br/search?keyword={nome.replace(' ', '+')}"

    with st.container(border=True):
        col_img, col_txt, col_btn = st.columns([1, 4, 1.5])
        
        with col_img:
            st.markdown(f"<h1 style='text-align: center;'>{ico}</h1>", unsafe_allow_html=True)
            
        with col_txt:
            st.markdown(f"### {nome}")
            st.markdown(f"💰 **Valor:** {valor} | 🏷️ **Ticket:** {ticket}")
            st.caption(f"📍 Destino: {link_final[:60]}...")
            
        with col_btn:
            st.metric("🔥 CALOR", f"{calor}°C")
            st.link_button("👁️ VER PRODUTO", link_final, use_container_width=True)
            
            if st.button("🎯 SELECIONAR", key=f"sel_{idx}", use_container_width=True):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link_final
                st.success("✅ PRODUTO NO ARSENAL!")
                st.rerun()

# --- 3. ACESSO E MOTOR IA ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Login</h1>", unsafe_allow_html=True)
    senha = st.text_input("Senha Master:", type="password")
    if st.button("LOGAR", use_container_width=True):
        if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')

if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- 4. INTERFACE ---
st.sidebar.title("🔱 Nexus Control")
mkt = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt
filtro_ticket = st.sidebar.multiselect("Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (A QUE PAROU DE FUNCIONAR) ---
with tabs[0]:
    st.header(f"🔍 Scanner de Elite: {mkt}")
    qtd = st.slider("Quantidade:", 5, 20, 10)
    
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando produtos e corrigindo links..."):
            # Prompt agressivo para a IA não conversar, apenas entregar dados
            prompt_scanner = f"""
            Aja como um minerador de tendências. Liste {qtd} produtos virais da {mkt}.
            Filtro de ticket: {filtro_ticket}.
            Retorne EXATAMENTE neste formato para cada:
            NOME: [nome] | VALOR: [preço] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url]
            Separe cada produto pelo marcador: ###
            """
            
            resultado = miny.minerar_produtos(prompt_scanner, mkt, st.session_state.motor_ia_obj)
            
            if resultado:
                # O SEGREDO: Limpeza de markdown que impedia a mineração
                res_clean = resultado.replace("**", "").replace("`", "").replace("[", "").replace("]", "")
                # Divide e garante que só pega blocos com nome
                st.session_state.lista_produtos = [p.strip() for p in res_clean.split("###") if "NOME:" in p.upper()]
                st.rerun()

    # Exibição dos cards minerados
    if st.session_state.lista_produtos:
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                # Fatiador robusto que aceita variações de escrita
                d = {}
                for item in bloco.split("|"):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        d[k.strip().upper()] = v.strip()
                
                # Renderização com dados extraídos
                renderizar_card_produto(
                    i, 
                    d.get("NOME", "Produto Detectado"), 
                    d.get("VALOR", "Consultar"), 
                    d.get("CALOR", "50"), 
                    d.get("TICKET", "Médio"),
