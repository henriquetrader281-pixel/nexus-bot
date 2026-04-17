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

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (LAYOUT ANTIGO RESTAURADO) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # LÓGICA DE LINK BLINDADO (Igual ao seu exemplo de sucesso)
    link_limpo = str(link).split('?')[0].strip()
    if "shopee" in link_limpo.lower():
        # Garante que o link termine exatamente como o que você mandou
        link_final = f"{link_limpo}?smtt=0.0.{ID_AFILIADO}"
    else:
        link_final = link_limpo if link_limpo.startswith("http") else f"https://shopee.com.br/search?keyword={nome.replace(' ', '+')}"

    with st.container(border=True):
        # Layout Horizontal da Versão Antiga
        col_img, col_txt, col_btn = st.columns([1, 4, 1.5])
        
        with col_img:
            st.markdown(f"<h1 style='text-align: center;'>{ico}</h1>", unsafe_allow_html=True)
            
        with col_txt:
            st.markdown(f"### {nome}")
            st.markdown(f"💰 **Valor:** {valor} | 🏷️ **Ticket:** {ticket}")
            st.caption(f"🔗 {link_final[:60]}...") # Mostra um pedaço do link real
            
        with col_btn:
            st.metric("🔥 CALOR", f"{calor}°C")
            # Botão de Ver Produto (Link Externo)
            st.link_button("👁️ VER PRODUTO", link_final, use_container_width=True)
            # Botão de Selecionar (Para o Arsenal)
            if st.button("🎯 SELECIONAR", key=f"sel_{idx}", use_container_width=True):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link_final
                st.success("✅ CAPTURADO!")
                st.rerun()

# --- 3. LOGIN E MOTOR IA ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Login</h1>", unsafe_allow_html=True)
    senha = st.text_input("Acesso Master:", type="password")
    if st.button("LOGAR", use_container_width=True):
        if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')

if "lista_produtos" not in st.session_state: st.session_state.lista_produtos = []

# --- 4. INTERFACE E SCANNER ---
st.sidebar.title("🔱 Nexus Control")
mkt = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt
tickets = st.sidebar.multiselect("Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

with tabs[0]:
    st.header(f"🔍 Scanner de Oportunidades - {mkt}")
    qtd = st.slider("Quantidade de produtos:", 5, 20, 10)
    
    if st.button("🚀 INICIAR MINERAÇÃO", use_container_width=True):
        with st.spinner("Minerando produtos virais..."):
            prompt = f"""
            Aja como um minerador de elite. Busque {qtd} produtos virais na {mkt} com ticket {tickets}.
            Formato OBRIGATÓRIO: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url]
            Separe cada produto por ###
            """
            res = miny.minerar_produtos(prompt, mkt, st.session_state.motor_ia_obj)
            if res:
                # Limpa lixo de markdown que trava o fatiador
                res_clean = res.replace("**", "").replace("`", "")
                st.session_state.lista_produtos = [p.strip() for p in res_clean.split("###") if "NOME:" in p.upper()]
                st.rerun()

    if st.session_state.lista_produtos:
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                d = {}
                for parte in bloco.split("|"):
                    if ":" in parte:
                        k, v = parte.split(":", 1)
                        d[k.strip().upper()] = v.strip()
                
                renderizar_card_produto(
                    i, 
                    d.get("NOME", "Produto"), 
                    d.get("VALOR", "Sob consulta"), 
                    d.get("CALOR", "50"), 
                    d.get("TICKET", "Médio"), 
                    d.get("LINK", "#"), 
                    mkt
                )
            except: continue

# --- CONEXÃO COM MÓDULOS ---
with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
with tabs[3]: studio_tab.exibir_estudio(miny, st.session_state.motor_ia_obj)
with tabs[4]: postador.exibir_postador()
with tabs[5]: update.dashboard_performance_simples()
