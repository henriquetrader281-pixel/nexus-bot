import streamlit as st
import arsenal
import trends
import pandas as pd
import update
import os
import urllib.parse
from datetime import datetime
import mineracao as miny
import estudio
import google.generativeai as genai
import json
import radar_engine

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- INTELIGÊNCIA DE TENDÊNCIAS ---
def get_nexus_intelligence():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"Analise tendências virais de HOJE ({hoje}) no TikTok Brasil e Instagram Reels. Retorne APENAS JSON."
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e)}

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS CORRIGIDA ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    # AJUSTE: Limpando o nome do produto (remove %20, acentos da URL e asteriscos)
    nome_limpo = urllib.parse.unquote(nome).replace("*", "").strip() if nome else "Produto Detectado"
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            st.markdown(f"**{ico} {nome_limpo}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
            
        with c2:
            try:
                c_string = "".join(filter(str.isdigit, str(calor)))
                calor_num = min(max(int(c_string), 0), 100) if c_string else 0
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
            
        with c3:
            # KEY ÚNICA: Adicionado valor e idx para evitar DuplicateElementId
            if st.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}_{valor[:5]}", use_container_width=True):
                st.session_state.sel_nome = nome_limpo
                st.session_state.sel_link = link
                st.session_state.sel_preco = valor
                update.registrar_mineracao(nome_limpo, link, calor_num)
                st.toast(f"Alvo Selecionado: {nome_limpo}")

# --- LOGIN E ESTADOS ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Acesso:", type="password", key="login_pass")
        if st.button("AUTENTICAR", use_container_width=True, key="btn_login_main"):
            if senha == st.secrets["NEXUS_PASSWORD"]:
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

def inicializar_motor_ia():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 'gemini-pro' é o modelo que não dá erro 404
        return genai.GenerativeModel('gemini-pro') 
    except Exception as e:
        st.error(f"Erro IA: {e}")
        return None

# --- 4. INICIALIZAÇÃO DO MOTOR IA ---
if "motor_ia_obj" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # COLOQUE A LINHA AQUI:
try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Erro ao carregar IA: {e}")

# --- SIDEBAR (Centralizada para evitar duplicidade) ---
with st.sidebar:
    st.title("🔱 Painel Nexus")
    # Centralizei o Marketplace aqui para evitar que ele seja recriado dentro das abas
    mkt = st.selectbox("Marketplace Alvo:", ["Shopee", "Amazon", "Mercado Livre"], key="mkt_global_select")
    st.session_state.mkt_global = mkt
    
    st.divider()
    if st.button("♻️ Resetar IA", key="btn_reset_sidebar"):
        st.session_state.motor_ia_obj = inicializar_motor_ia()
        st.rerun()

# --- INTERFACE DE ABAS ---
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🌍 RADAR", "🎥 ESTÚDIO", "📊 DASHBOARD"])

with tabs[0]: # SCANNER
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True, key="btn_start_scan"):
        with st.spinner("Minerando..."):
            prompt = f"Liste 10 produtos virais da {mkt}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt, mkt, "groq")

    if st.session_state.get("res_busca"):
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            if "|" in linha:
                try:
                    partes = linha.replace("**", "").split("|")
                    d = {}
                    for p in partes:
                        if ":" in p:
                            chave, valor_p = p.split(":", 1) 
                            d[chave.strip().upper()] = valor_p.strip()
                    
                    # Chama a função com o nome que será limpo lá dentro
                    renderizar_card_produto(idx, d.get("NOME", "Produto"), d.get("VALOR", "---"), d.get("CALOR", "50"), d.get("TICKET", "Médio"), d.get("URL", "#"), mkt)
                except: continue

with tabs[1]: # ARSENAL
    arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)

with tabs[2]: # TRENDS
    trends.exibir_trends()

with tabs[3]: # RADAR
    radar_engine.exibir_radar()

with tabs[4]: # ESTÚDIO
    st.info("🎥 Módulo de Estúdio ligado ao Arsenal.")

with tabs[5]: # DASHBOARD
    st.info("📊 Performance e Cliques em tempo real.")
