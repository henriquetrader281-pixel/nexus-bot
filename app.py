import streamlit as st
import arsenal 
import trends
import estudio
import pandas as pd
import update
import radar_engine 
import os
import urllib.parse
from datetime import datetime
import mineracao as miny

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"**{ico} {nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        
        with c2:
            try:
                calor_num = min(max(int(calor), 0), 100)
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", width='stretch'):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.toast(f"Alvo Selecionado: {nome}")

# --- 3. SISTEMA DE ACESSO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Acesso:", type="password")
        if st.button("AUTENTICAR", width='stretch'):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado:
    login()

# --- 4. ESTADO DA SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox(
    "Marketplace Ativo:", 
    ["Shopee", "Mercado Livre", "Amazon"], 
    index=["Shopee", "Mercado Livre", "Amazon"].index(st.session_state.mkt_global)
)

motor_ia = st.sidebar.selectbox("Cérebro de IA:", ["gpt-4o-mini", "gemini-1.5-pro"])

# Linha 79: Definição das 6 Abas
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Volume de Mineração:", [15, 30, 45], index=1)
    
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho da Operação:", value="Cozinha Criativa", key="nicho_input")

    if st.button(f"🔥 INICIAR VARREDURA {st.session_state.mkt_global.upper()}", width='stretch'):
        with st.spinner(f"Nexus minerando produtos virais em '{foco_nicho}'..."):
            prompt_scanner = f"""
            Liste {qtd_produtos} produtos físicos da {st.session_state.mkt_global} para o nicho '{foco_nicho}'.
            Formato por linha: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]
            """
            resultado = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
            st.session_state.res_busca = resultado
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            linha_limpa = linha.replace("**", "").replace("*", "").strip()
            
            if "|" in linha_limpa:
                try:
                    partes_lista = [p.strip() for p in linha_limpa.split('|')]
                    dados = {}
                    for p in partes_lista:
                        if ':' in p:
                            k, v = p.split(':', 1)
                            dados[k.strip().upper()] = v.strip()
                    
                    nome_final = "Produto Desconhecido"
                    for chave in dados.keys():
                        if "NOME" in chave:
                            nome_final = dados[chave]
                            break
                    
                    if nome_final == "Produto Desconhecido" and partes_lista:
                        nome_final = partes_lista[0].replace("NOME:", "").strip()

                    ticket_val = "Médio"
                    for chave in dados.keys():
                        if "TICKET" in chave: ticket_val = dados[chave]; break
                    
                    if ticket_val in filtro_ticket:
                        c_str = "".join(filter(str.isdigit, str(dados.get("CALOR", "0"))))
                        
                        renderizar_card_produto(
                            idx, 
                            nome_final, 
                            dados.get("VALOR", "R$ ---"), 
                            int(c_str) if c_str else 0, 
                            ticket_val, 
                            dados.get("URL", "#"), 
                            st.session_state.mkt_global
                        )
                except:
                    continue

# --- ABA 1: ARSENAL ---
with tabs[1]:  
    arsenal.exibir_arsenal(miny, motor_ia)

# --- ABA 2: TRENDS (Spotify) ---
with tabs[2]:
    trends.exibir_trends()

# --- ABA 3: ESTÚDIO ---
with tabs[3]:
    estudio.exibir_estudio(miny, motor_ia)

# --- ABA 4: DASHBOARD ---
with tabs[4]:
    st.header("📊 Dashboard de Performance")
    try:
        update.dashboard_performance_simples()
    except Exception as e:
        st.error(f"Erro ao carregar Dashboard: {e}")

# --- ABA 5: RADAR ---
with tabs[5]:
    st.header("🌍 Inteligência Radar")
    c_eua, c_br = st.columns(2)
    if c_eua.button("🇺🇸 Scanner TikTok USA", width='stretch'): 
        st.info("Buscando tendências internacionais...")
    if c_br.button(f"🇧🇷 Trends {st.session_state.mkt_global}", width='stretch'): 
        st.success("Analisando volume de buscas Brasil...")
