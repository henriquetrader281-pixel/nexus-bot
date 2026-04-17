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

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (LAYOUT V101 ORIGINAL) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # Limpeza de Link e Injeção de ID
    link_limpo = str(link).replace("]", "").replace("[", "").replace(" ", "").strip()
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
                st.success("✅ CAPTURADO!")
                st.rerun()

# --- 3. LOGIN E MOTOR IA ---
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

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner de Elite: {mkt}")
    qtd = st.slider("Quantidade:", 5, 20, 10)
    
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando produtos..."):
            prompt_scanner = f"Busque {qtd} produtos virais na {mkt}. Formato: NOME: [nome] | VALOR: [R$] | CALOR: [0-100] | TICKET: [Baixo/Médio/Alto] | LINK: [url]. Separe por ###"
            resultado = miny.minerar_produtos(prompt_scanner, mkt, st.session_state.motor_ia_obj)
            if resultado:
                res_clean = resultado.replace("**", "").replace("`", "")
                st.session_state.lista_produtos = [p.strip() for p in res_clean.split("###") if "NOME:" in p.upper()]
                st.rerun()

    if st.session_state.lista_produtos:
        for i, bloco in enumerate(st.session_state.lista_produtos):
            try:
                d = {}
                for item in bloco.split("|"):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        d[k.strip().upper()] = v.strip()
                
                # AQUI ESTAVA O ERRO: Chamada agora fechada corretamente
                renderizar_card_produto(
                    i, 
                    d.get("NOME", "Produto"), 
                    d.get("VALOR", "---"), 
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
