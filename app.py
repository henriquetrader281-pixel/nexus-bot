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

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (ALINHAMENTO FIXADO) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
with c1:
            # Esta linha abaixo precisa de 4 espaços (ou 1 Tab) a mais que o 'with'
            n_exibir = urllib.parse.unquote(nome).replace("*", "").strip() if nome else "Produto Detectado"
            st.markdown(f"**{ico} {n_exibir}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
with c2:
            try:
                c_string = "".join(filter(str.isdigit, str(calor)))
                calor_num = min(max(int(c_string), 0), 100) if c_string else 0
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", use_container_width=True):
            st.session_state.sel_nome = n_exibir
            st.session_state.sel_link = link
            st.session_state.sel_preco = valor
            update.registrar_mineracao(n_exibir, link, calor_num)
            st.toast(f"Alvo Selecionado: {n_exibir}")

# --- LOGIN E ESTADOS ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Acesso:", type="password")
        if st.button("AUTENTICAR", use_container_width=True):
            if senha == st.secrets["NEXUS_PASSWORD"]:
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

# --- INICIALIZAÇÃO BLINDADA DO GEMINI ---
if "motor_ia_obj" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # AQUI ESTÁ A CHAVE: Nome puro, sem 'models/' e sem 'v1beta' no objeto
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Falha crítica na configuração da IA: {e}")

# --- INTERFACE (Abas Reduzidas para o que é usado) ---
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "📊 DASHBOARD"])

with tabs[0]:
    mkt = st.sidebar.selectbox("Marketplace:", ["Shopee", "Amazon", "Mercado Livre"])
    st.session_state.mkt_global = mkt
    if st.button("🚀 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando..."):
            prompt = f"Liste 10 produtos virais da {mkt}. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt, mkt, "groq")

    if st.session_state.get("res_busca"):
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            if "|" in linha:
                try:
                    # Fatiador blindado que preserva o link completo
                    partes = linha.replace("**", "").split("|")
                    d = {}
                    for p in partes:
                        if ":" in p:
                            chave, valor = p.split(":", 1) 
                            d[chave.strip().upper()] = valor.strip()
                    
                    renderizar_card_produto(idx, d.get("NOME", "Produto"), d.get("VALOR", "---"), d.get("CALOR", "50"), d.get("TICKET", "Médio"), d.get("URL", "#"), mkt)
                except: continue

with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
with tabs[3]: st.info("🎥 Módulo de Estúdio ligado ao Arsenal.")
with tabs[4]: st.info("📊 **Dashboard:** Monitoramento de cliques e conversões em tempo real.")
