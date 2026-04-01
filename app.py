import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO E SEGURANÇA (Legacy app 1, 2, 4) ---
st.set_page_config(page_title="Nexus Absolute V35.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔐 Nexus Private Access</h1>", unsafe_allow_html=True)
    with st.form("login"):
        e = st.text_input("E-mail Autorizado:")
        s = st.text_input("Senha Mestre:", type="password")
        if st.form_submit_button("Liberar Nexus", use_container_width=True):
            autorizados = st.secrets.get("ALLOWED_USERS", "").split(",")
            if e in [i.strip() for i in autorizados] and s == st.secrets["NEXUS_PASSWORD"]:
                st.session_state["autenticado"] = True
                st.session_state["user_email"] = e
                st.rerun()
            else: st.error("Acesso Negado.")
    st.stop()

# --- 2. MOTORES IA & DATASET ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data","produto","roteiro","link","views","cliques","ctr","status","score"]).to_csv(DATA_PATH, index=False)

def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}]).choices[0].message.content

def ad_scorer(roteiro): # Resgate V16
    prompt = f"Dê uma nota de 0 a 100 para este roteiro de TikTok Ads: {roteiro}. Retorne apenas o número."
    try:
        nota = gerar_ia(prompt)
        return int(''.join(filter(str.isdigit, nota)))
    except: return 75

# --- 3. INTERFACE OPERACIONAL V35 ---
st.title("🔱 Nexus Brain: Global Intelligence V35.0")
st.caption(f"Operador: {st.session_state.get('user_email')} | Mineração Cruzada BR + EUA Ativa")

tabs = st.tabs(["🌎 Mineração Global", "🎥 Arsenal & Scoring", "💬 Funil", "📊 Escala & ROI", "🕹️ Central"])

with tabs[0]: # [PATCH 08] MINERAÇÃO CRUZADA BR & EUA
    st.header("🎯 Tendências Cruzadas (Shopee + Google Search)")
    col_reg1, col_reg2 = st.columns(2)
    
    with col_reg1:
        if st.button("🇧🇷 Escanear Top 10 Brasil", use_container_width=True):
            with st.status("Minerando Brasil..."):
                prompt = "Liste 10 produtos buscados na Shopee Brasil hoje. Tabela com: Rank, Produto, Tendência Google e Link de Busca (https://shopee.com.br/search?keyword=...)."
                st.session_state['trends_br'] = gerar_ia(prompt)
    
    with col_reg2:
        if st.button("🇺🇸 Escanear Top 10 EUA", use_container_width=True):
            with st.status("Minerando EUA..."):
                prompt = "Identifique 10 produtos virais no TikTok Shop/Amazon USA hoje. Tabela com: Rank, Produto EUA, Por que é Viral e Link de Busca (https://shopee.com.br/search?keyword=...)."
                st.session_state['trends_usa'] = gerar_ia(prompt)

    st.divider()
    c_br, c_usa = st.columns(2)
    with c_br:
        if 'trends_br' in st.session_state: st.markdown(st.session_state['trends_br'])
    with c_usa:
        if 'trends_usa' in st.session_state: st.markdown(st.session_state['trends_usa'])

with tabs[1]: # AR
