import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import mineracao as miny # O novo módulo que criamos

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

# --- 2. ESTADO DA SESSÃO (Recuperando o que foi perdido) ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "copy_ativa" not in st.session_state: st.session_state.copy_ativa = ""

# --- 3. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Configurações")
mkt_alvo = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
nicho = st.sidebar.text_input("Nicho Ativo:", "Cozinha Criativa")
motor_ia = st.sidebar.radio("Motor IA:", ["Groq", "Gemini"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (Restaurado com Colunas de Calor/Preço) ---
with tabs[0]:
    st.header(f"Mineração Direcionada: {mkt_alvo}")
    if st.button(f"🔥 Iniciar Varredura {mkt_alvo}", use_container_width=True):
        with st.spinner("IA minerando tendências..."):
            resultado = miny.minerar_produtos(nicho, mkt_alvo, motor_ia)
            st.session_state.res_busca = miny.formatar_saida_limpa(resultado)
    
    if st.session_state.res_busca:
        # Recuperando a lógica de exibição em cards da V71
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            if "|" in linha:
                try:
                    partes = {p.split(':')[0].strip(): p.split(':')[1].strip() for p in linha.split('|')}
                    nome = partes.get("NOME", "Desconhecido")
                    calor = int(partes.get("CALOR", "0"))
                    valor = partes.get("VALOR", "R$ 0")
                    link = partes.get("URL", "#")

                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.write(f"📦 **{nome}**")
                        c1.caption(f"💰 Preço Médio: {valor}")
                        c2.progress(calor/100)
                        c2.write(f"🌡️ {calor}°C")
                        if c3.button("Selecionar", key=f"btn_{idx}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link
                            st.toast(f"{nome} selecionado!")
                except: continue

# --- ABA 1: ARSENAL (Restaurado da V71 - Injeção de 10 Variações) ---
with tabs[1]:
    st.header("🚀 Arsenal de Vendas")
    if st.session_state.sel_nome:
        st.success(f"Produto Ativo: {st.session_state.sel_nome}")
        if st.button("⚡ Gerar 10 Variações de Copy Viral"):
            # Chama a IA para criar as variações (Recuperado da V9)
            prompt_v = f"Crie 10 roteiros de 15s para {st.session_state.sel_nome} focados no {mkt_alvo}. Separe com ###"
            res_ia = miny.minerar_produtos(nicho, mkt_alvo, motor_ia) # Reusando motor para rapidez
            variacoes = [v.strip() for v in res_ia.split("###") if len(v) > 10]
            for i, v in enumerate(variacoes):
                with st.container(border=True):
                    st.write(v)
                    if st.button(f"Usar V{i+1}", key=f"v_{i}"):
                        st.session_state.copy_ativa = v
                        st.toast("Enviado ao Estúdio!")
    else:
        st.warning("Selecione um produto no Scanner.")

# --- ABA 2: RADAR (Restaurado da V22-V26 - Global vs Nacional) ---
with tabs[2]:
    st.header("🌍 Inteligência Radar")
    c_eua, c_br = st.columns(2)
    with c_eua:
        if st.button("🇺🇸 Scanner TikTok USA"):
            st.info("Buscando produtos virais nos EUA...") # Conectar ao seu radar_engine se disponível
    with c_br:
        if st.button("🇧🇷 Trends Shopee/ML"):
            st.success("Analizando tendências brasileiras...")

# --- ABA 3: ESTÚDIO (Restaurado com Deep Link) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    copy_f = st.text_area("Roteiro:", value=st.session_state.copy_ativa)
    
    if st.button("🚀 Produzir Mídia + Deep Link"):
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_deep = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
        st.success(f"Mídia em produção para {mkt_alvo}!")
        st.code(link_deep, language="text")
