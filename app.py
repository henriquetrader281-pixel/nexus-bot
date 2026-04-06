import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Absolute V82", layout="wide", page_icon="🔱")

# --- LOGIN SEGURO VIA SECRETS ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Puxa a senha do Secrets (Campo: NEXUS_PASSWORD)
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Insira a senha de acesso:", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- CONEXÕES VIA SECRETS (Groq & Gemini) ---
try:
    # Motor 1: Groq (Llama 3.3)
    client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Motor 2: Preparado para Gemini (Configurar GEMINI_API_KEY no Secrets)
    # Aqui vamos importar e configurar o módulo do Gemini na próxima etapa
    gemini_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception as e:
    st.error("⚠️ Verifique as Chaves de API (Groq/Gemini) nos Secrets do Streamlit.")

# --- MEMÓRIA DE SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "motor_ia" not in st.session_state: st.session_state.motor_ia = "Groq"

# --- FUNÇÕES DE INTELIGÊNCIA ---
def gerar_ia_groq(prompt):
    res = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"system", "content":"Data Miner Mode: Apenas dados puros e ícones."},
                  {"role":"user","content": prompt}]
    )
    return res.choices[0].message.content

def gerar_ia_gemini(prompt):
    """Espaço reservado para a lógica .py do Gemini que vamos programar"""
    # Quando o script do Gemini estiver pronto, ele entrará aqui
    return "Motor Gemini aguardando integração do arquivo .py..."

# --- INTERFACE PRINCIPAL ---
st.title("🔱 Nexus Absolute: Multi-Engine Intelligence")

# Seletor de Cérebro (Para usarmos o Gemini na programação avançada depois)
st.sidebar.title("⚙️ Configurações")
st.session_state.motor_ia = st.sidebar.selectbox("Motor de IA Ativo:", ["Groq", "Gemini (Beta)"])

tabs = st.tabs(["🔎 Scanner 30x", "⚔️ Arsenal 10x", "🔥 Radar Global", "🎥 Estúdio IA", "💰 Dashboard"])

# --- ABA 0: SCANNER (Sincronizado com Secrets) ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências")
    c1, c2, c3 = st.columns([2, 1, 1])
    nicho = c1.text_input("Nicho:", value="Cozinha Criativa")
    ticket = c2.selectbox("Ticket:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Iniciar Mineração", use_container_width=True):
        with st.status(f"Minerando via {st.session_state.motor_ia}..."):
            prompt = f"Liste 30 produtos de {nicho} na Shopee BR. Formato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"
            
            if st.session_state.motor_ia == "Groq":
                st.session_state.res_busca = gerar_ia_groq(prompt)
            else:
                st.session_state.res_busca = gerar_ia_gemini(prompt)
            st.rerun()

    if st.session_state.res_busca:
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha and "NOME:" in linha:
                try:
                    p = linha.split("|")
                    nome = p[0].split("NOME:")[1].strip()
                    calor = int(''.join(filter(str.isdigit, p[1])))
                    valor = p[2].split("VALOR:")[1].strip()
                    cresc = p[3].split("CRESC:")[1].strip()
                    link_orig = p[4].split("URL:")[1].strip()
                    
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"📦 **{nome}**")
                            st.caption(f"💰 Ticket: {valor} | 📈 Cresc: {cresc}")
                        with col2:
                            st.write(f"🌡️ {calor}°C")
                            st.progress(min(calor/100, 1.0))
                        with col3:
                            st.markdown("🔥 `EXPLOSÃO`" if calor > 80 else "✅ `ESTÁVEL`")
                        with col4:
                            if st.button("Selecionar", key=f"sel_{idx}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link_orig
                                st.toast(f"✅ {nome} carregado!")
                except: continue

# --- ABA 1: ARSENAL (Munição de Copy) ---
with tabs[1]:
    st.header("⚔️ Arsenal de Escala 10x")
    if st.session_state.sel_nome:
        st.success(f"Alvo Selecionado: {st.session_state.sel_nome}")
        if st.button("🔥 DISPARAR 10 VARIAÇÕES"):
            prompt_ars = f"Crie 10 roteiros de 15s para {st.session_state.sel_nome}. Separe com ###"
            variacoes = [v.strip() for v in gerar_ia_groq(prompt_ars).split("###") if len(v) > 10]
            for i, v in enumerate(variacoes):
                with st.container(border=True):
                    st.write(f"**V{i+1}**")
                    st.write(v)
    else: st.warning("Selecione um produto no Scanner.")

# --- ABA 3: ESTÚDIO (Conectado ao Secrets) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    if st.button("🚀 Produzir Mídia via Webhook"):
        webhook = st.secrets.get("WEBHOOK_POST_URL")
        aff_id = st.secrets.get("SHOPEE_ID")
        if webhook:
            link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
            requests.post(webhook, json={"prod": st.session_state.sel_nome, "link": link_final})
            st.success("Ordem enviada!")
