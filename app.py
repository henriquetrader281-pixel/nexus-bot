import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import mineracao as miny # O novo módulo que criamos

# --- FUNÇÃO DE MELHORIA: UPDATE DE LINHA (REUTILIZÁVEL) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "📦", "Mercado Livre": "🏪", "Amazon": "🛒"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{ico} **{nome}**")
        c1.caption(f"💰 {valor} | 🎫 {ticket} | 🏷️ {mkt_alvo}")
        
        # Trava de segurança para o calor (Max 100)
        calor_limpo = min(max(int(calor), 0), 99)
        c2.progress(calor_limpo/100)
        c2.write(f"🌡️ {calor_limpo}°C")
        
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

# --- 3. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Configurações")
mkt_alvo = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
nicho = st.sidebar.text_input("Nicho Ativo:", "Cozinha Criativa")
motor_ia = st.sidebar.radio("Motor IA:", ["Groq", "Gemini"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (ATUALIZADA) ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {mkt_alvo}")
    
    # SELETORES RÁPIDOS DE MARKETPLACE (ESTILO IMAGEM)
    c_mkt1, c_mkt2, c_mkt3 = st.columns(3)
    if c_mkt1.button("🧡 Shopee", use_container_width=True): mkt_alvo = "Shopee"
    if c_mkt2.button("💛 Mercado Livre", use_container_width=True): mkt_alvo = "Mercado Livre"
    if c_mkt3.button("💙 Amazon", use_container_width=True): mkt_alvo = "Amazon"

    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Quantidade de itens:", [15, 30, 45], index=1)
        st.caption(f"Foco: {nicho}")

    if st.button(f"🔥 Iniciar Varredura na {mkt_alvo}", use_container_width=True):
        with st.spinner(f"IA minerando tendências na {mkt_alvo}..."):
            resultado = miny.minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=qtd_produtos)
            st.session_state.res_busca = miny.formatar_saida_limpa(resultado)
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Visualizar Tickets:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            if "|" in linha and "NOME" in linha.upper():
                try:
                    # Extração de dados da linha
                    partes = {p.split(':')[0].strip().upper(): p.split(':')[1].strip() for p in linha.split('|') if ':' in p}
                    
                    ticket_atual = partes.get("TICKET", "Médio")
                    if ticket_atual in filtro_ticket:
                        # CHAMADA DA FUNÇÃO DE UPDATE DE LINHA (MELHORIA)
                        calor_val = "".join(filter(str.isdigit, partes.get("CALOR", "0")))
                        renderizar_card_produto(
                            idx, 
                            partes.get("NOME", "Produto"), 
                            partes.get("VALOR", "Sob consulta"), 
                            int(calor_val) if calor_val else 0,
                            ticket_atual,
                            partes.get("URL", "#"),
                            mkt_alvo
                        )
                except: continue

# --- ABA 1: ARSENAL ---
with tabs[1]:
    st.header("🚀 Arsenal de Vendas")
    if st.session_state.sel_nome:
        st.success(f"Produto Ativo: {st.session_state.sel_nome} ({mkt_alvo})")
        if st.button(f"⚡ Gerar 10 Copies para {mkt_alvo}"):
            res_ia = miny.minerar_produtos(f"Gere 10 variações de copy viral para: {st.session_state.sel_nome}", mkt_alvo, motor_ia) 
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
    with c_eua:
        if st.button("🇺🇸 Scanner TikTok USA"):
            st.info("Buscando produtos virais nos EUA...")
    with c_br:
        if st.button(f"🇧🇷 Trends {mkt_alvo}"):
            st.success(f"Analisando tendências na {mkt_alvo}...")

# --- ABA 3: ESTÚDIO ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    copy_f = st.text_area("Roteiro:", value=st.session_state.copy_ativa)
    
    if st.button(f"🚀 Produzir Mídia para {mkt_alvo}"):
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_deep = f"Link de Afiliado {mkt_alvo}: {st.session_state.sel_link}"
        st.success(f"Mídia em produção para {mkt_alvo}!")
        st.code(link_deep, language="text")
