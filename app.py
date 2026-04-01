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
    prompt = f"Dê uma nota de 0 a 100 para este roteiro de TikTok Ads (Retenção e CTA): {roteiro}. Retorne apenas o número."
    try:
        nota = gerar_ia(prompt)
        return int(''.join(filter(str.isdigit, nota)))
    except: return 75

# --- 3. INTERFACE OPERACIONAL V35 ---
st.title("🔱 Nexus Brain: Global Intelligence V35.0")
st.caption(f"Operador: {st.session_state.get('user_email')} | Mineração Cruzada BR + EUA Ativa")

tabs = st.tabs(["🌎 Mineração Global", "🎥 Arsenal & Scoring", "💬 Funil de Comentários", "📊 Escala & ROI", "🕹️ Central"])

with tabs[0]: # [PATCH 08] MINERAÇÃO CRUZADA BR & EUA
    st.header("🎯 Tendências Cruzadas (Shopee + Google Search)")
    
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        if st.button("🇧🇷 Escanear Top 10 Brasil", use_container_width=True):
            with st.status("Cruzando dados Shopee BR + Google Trends..."):
                prompt = """Aja como Analista de E-commerce. Identifique os 10 produtos mais buscados na Shopee Brasil hoje. 
                Cruze com o volume do Google. Gere uma Tabela Markdown com: 
                | Rank | Produto | Tendência Google | Link de Busca (https://shopee.com.br/search?keyword=...) |"""
                st.session_state['trends_br'] = gerar_ia(prompt)
    
    with col_reg2:
        if st.button("🇺🇸 Escanear Top 10 EUA (TikTok/Amazon)", use_container_width=True):
            with st.status("Minerando tendências virais nos EUA..."):
                prompt = """Identifique 10 produtos que estão viralizando no TikTok Shop e Amazon USA hoje. 
                Gere uma Tabela Markdown com: 
                | Rank | Produto EUA | Por que é Viral | Link de Busca (https://shopee.com.br/search?keyword=...) |"""
                st.session_state['trends_usa'] = gerar_ia(prompt)

    st.divider()
    c_br, c_usa = st.columns(2)
    with c_br:
        if 'trends_br' in st.session_state:
            st.subheader("📍 Mercado Brasileiro")
            st.markdown(st.session_state['trends_br'])
    with c_usa:
        if 'trends_usa' in st.session_state:
            st.subheader("📍 Mercado Americano (Target)")
            st.markdown(st.session_state['trends_usa'])

with tabs[1]: # ARSENAL COM SCORING
    st.header("🚀 Criador de Arsenal (V16 Scorer)")
    p_nome = st.text_input("Nome do Produto Selecionado:")
    p_link = st.text_input("Link Shopee para Afiliar:")
    
    if st.button("🔥 Gerar Criativos com Nota"):
        link_limpo = p_link.split('?')[0]
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(link_limpo)}&aff_id={aff_id}"
        st.session_state['link_ativo'] = link_final
        
        res = gerar_ia(f"Crie 5 roteiros TikTok para {p_nome}. Separe por ###")
        df = pd.read_csv(DATA_PATH)
        for r in res.split("###"):
            if len(r) > 10:
                nota = ad_scorer(r)
                st.metric(f"Score da Variação", f"{nota}/100")
                st.write(r)
                novo = {"data": datetime.now().
