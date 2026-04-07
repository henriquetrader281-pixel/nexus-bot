import streamlit as st
import arsenal  # Importação do novo módulo
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import mineracao as miny

# --- FUNÇÃO DE RENDERIZAÇÃO ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "📦", "Mercado Livre": "🏪", "Amazon": "🛒"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{ico} **{nome}**")
        c1.caption(f"💰 {valor} | 🎫 {ticket} | 🏷️ {mkt_alvo}")
        
        calor_num = min(max(int(calor), 0), 100)
        c2.progress(calor_num / 100)
        c2.write(f"🌡️ {calor_num}°C")
        
        if c3.button("Selecionar", key=f"btn_{idx}_{mkt_alvo}"):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.toast(f"Selecionado: {nome}")

# --- 1. CONFIGURAÇÃO E LOGIN ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Acesso:", type="password")
        if st.button("Entrar", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

if not st.session_state.autenticado: login()

# --- 2. ESTADO DA SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "copy_ativa" not in st.session_state: st.session_state.copy_ativa = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

# --- 3. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Configurações")
# Marketplace na sidebar (sem conflito)
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"], index=["Shopee", "Mercado Livre", "Amazon"].index(st.session_state.mkt_global))

# CORREÇÃO: Mostramos o nicho na sidebar apenas como informação para não dar erro de duplicidade
st.sidebar.info(f"Nicho Atual: {st.session_state.get('nicho_ativo', 'Cozinha Criativa')}")
motor_ia = st.sidebar.radio("Motor IA:", ["Groq", "Gemini"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    # SELETORES RÁPIDOS
    c_mkt1, c_mkt2, c_mkt3 = st.columns(3)
    if c_mkt1.button("🧡 Shopee", use_container_width=True): 
        st.session_state.mkt_global = "Shopee"
        st.rerun()
    if c_mkt2.button("💛 Mercado Livre", use_container_width=True): 
        st.session_state.mkt_global = "Mercado Livre"
        st.rerun()
    if c_mkt3.button("💙 Amazon", use_container_width=True): 
        st.session_state.mkt_global = "Amazon"
        st.rerun()

    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Quantidade de itens:", [15, 30, 45], index=1)
    
    with col_sel2:
        # A ÚNICA KEY "nicho_ativo" DO APP FICA AQUI
        foco_nicho = st.text_input("🎯 Foco do Scanner (Mudar Nicho):", value="Cozinha Criativa", key="nicho_ativo")

    if st.button(f"🔥 Iniciar Varredura na {st.session_state.mkt_global}", use_container_width=True):
        with st.spinner(f"IA minerando {qtd_produtos} produtos em '{foco_nicho}'..."):
            resultado = miny.minerar_produtos(foco_nicho, st.session_state.mkt_global, motor_ia, qtd=qtd_produtos)
            st.session_state.res_busca = miny.formatar_saida_limpa(resultado)
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Visualizar Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            if "|" in linha and "NOME" in linha.upper():
                try:
                    partes = {p.split(':')[0].strip().upper(): p.split(':')[1].strip() for p in linha.split('|') if ':' in p}
                    ticket_atual = partes.get("TICKET", "Médio")
                    if ticket_atual in filtro_ticket:
                        c_str = "".join(filter(str.isdigit, partes.get("CALOR", "0")))
                        renderizar_card_produto(
                            idx, 
                            partes.get("NOME", "Produto"), 
                            partes.get("VALOR", "Consultar"), 
                            int(c_str) if c_str else 0,
                            ticket_atual,
                            partes.get("URL", "#"),
                            st.session_state.mkt_global
                        )
                except: continue

# --- ABA 1: ARSENAL ---
with tabs[1]:
    st.header("🚀 Arsenal de Vendas")
    if st.session_state.sel_nome:
        st.success(f"Produto Ativo: {st.session_state.sel_nome} ({st.session_state.mkt_global})")
        if st.button(f"⚡ Gerar 10 Copies para {st.session_state.mkt_global}"):
            res_ia = miny.minerar_produtos(f"Gere 10 variações de copy viral para: {st.session_state.sel_nome}", st.session_state.mkt_global, motor_ia) 
            variacoes = [v.strip() for v in res_ia.split("###") if len(v) > 10]
            if not variacoes: variacoes = res_ia.split('\n')
            for i, v in enumerate(variacoes):
                if len(v.strip()) > 5:
                    with st.container(border=True):
                        st.write(v)
                        if st.button(f"Usar V{i+1}", key=f"v_{i}"):
                            st.session_state.copy_ativa = v
                            st.toast("Enviado ao Estúdio!")
    else:
        st.warning("Selecione um produto no Scanner.")

# --- ABA 2: RADAR ---
with tabs[2]:
    st.header("🌍 Inteligência Radar")
    c_eua, c_br = st.columns(2)
    if c_eua.button("🇺🇸 Scanner TikTok USA"): st.info("Buscando produtos virais nos EUA...")
    if c_br.button(f"🇧🇷 Trends {st.session_state.mkt_global}"): st.success(f"Analisando tendências na {st.session_state.mkt_global}...")

# --- ABA 3: ESTÚDIO ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    st.text_input("Produto:", value=st.session_state.sel_nome)
    st.text_area("Roteiro:", value=st.session_state.copy_ativa)
    if st.button(f"🚀 Produzir Mídia para {st.session_state.mkt_global}"):
        st.success(f"Mídia em produção para {st.session_state.mkt_global}!")
        st.code(f"Link: {st.session_state.sel_link}", language="text")
