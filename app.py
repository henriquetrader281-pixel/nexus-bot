import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import mineracao as miny # O novo módulo que criamos

def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "📦", "Mercado Livre": "🏪", "Amazon": "🛒"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{ico} **{nome}**")
        c1.caption(f"💰 {valor} | 🎫 {ticket} | 🏷️ {mkt_alvo}")
        c2.progress(min(max(calor/100, 0.0), 1.0))
        c2.write(f"🌡️ {calor}°C")
        if c3.button("Selecionar", key=f"btn_{idx}"):
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
# O seletor que manda no app todo:
mkt_alvo = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
nicho = st.sidebar.text_input("Nicho Ativo:", "Cozinha Criativa")
motor_ia = st.sidebar.radio("Motor IA:", ["Groq", "Gemini"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

# --- ABA 0: SCANNER (ATUALIZADA COM MERCADO LIVRE/AMAZON) ---
with tabs[0]:
    # Título dinâmico que muda conforme o Marketplace escolhido
    st.header(f"🔍 Scanner Nexus: {mkt_alvo}")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Quantidade de itens:", [15, 30, 45], index=1)
        st.caption(f"Foco: {nicho}")

    # O botão agora indica o Marketplace específico
    if st.button(f"🔥 Iniciar Varredura na {mkt_alvo}", use_container_width=True):
        with st.spinner(f"IA minerando {qtd_produtos} produtos na {mkt_alvo}..."):
            resultado = miny.minerar_produtos(nicho, mkt_alvo, motor_ia, qtd=qtd_produtos)
            st.session_state.res_busca = miny.formatar_saida_limpa(resultado)
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect(
            "Visualizar Tickets:", 
            ["Baixo", "Médio", "Alto"], 
            default=["Baixo", "Médio", "Alto"]
        )
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            if "|" in linha and "NOME" in linha.upper():
                try:
                    partes = {}
                    for p in linha.split('|'):
                        if ":" in p:
                            chave, valor = p.split(':', 1)
                            k = chave.replace("*", "").strip().upper()
                            v = valor.replace("*", "").strip()
                            partes[k] = v

                    ticket_atual = partes.get("TICKET", "Médio")
                    if ticket_atual in filtro_ticket:
                        nome = partes.get("NOME", "Produto Sem Nome")
                        calor_str = partes.get("CALOR", "0")
                        calor_num = "".join(filter(str.isdigit, calor_str))
                        calor = int(calor_num) if calor_num else 0
                        
                        valor = partes.get("VALOR", "Consulte")
                        link = partes.get("URL", "#")

                        with st.container(border=True):
                            c1, c2, c3 = st.columns([2, 1, 1])
                            # Ícone muda conforme o Marketplace
                            icone = "📦" if mkt_alvo == "Shopee" else "🏪" if mkt_alvo == "Mercado Livre" else "🛒"
                            c1.write(f"{icone} **{nome}**")
                            c1.caption(f"💰 {valor} | 🎫 Ticket: {ticket_atual} | 🏷️ {mkt_alvo}")
                            
                            prog_calor = min(max(calor/100, 0.0), 1.0)
                            c2.progress(prog_calor)
                            c2.write(f"🌡️ {calor}°C")
                            
                            if c3.button("Selecionar", key=f"btn_{idx}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link
                                st.toast(f"{nome} da {mkt_alvo} selecionado!")
                except:
                    continue

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
