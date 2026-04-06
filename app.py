import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- 1. CONFIGURAÇÃO E LOGIN (SECRETS) ---
st.set_page_config(page_title="Nexus Absolute V90", layout="wide", page_icon="🔱")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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

# --- 2. CONEXÃO COM MOTORES (GROQ & GEMINI) ---
try:
    # Motor Groq vindo do Secrets
    client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Integração Gemini: Importa se o arquivo existir, senão avisa
    try:
        from gemini_engine import perguntar_gemini
        HAS_GEMINI = True
    except ImportError:
        HAS_GEMINI = False
except Exception as e:
    st.error("⚠️ Erro nas Chaves de API. Verifique o Secrets.")

# --- 3. MEMÓRIA DE SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "copy_ativa" not in st.session_state: st.session_state.copy_ativa = ""

# --- 4. FUNÇÃO DE IA UNIFICADA ---
def gerar_ia(prompt, system_msg="Você é um especialista em e-commerce. Seja direto."):
    if st.session_state.motor_ia == "Groq":
        res = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content": system_msg}, {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    elif st.session_state.motor_ia == "Gemini" and HAS_GEMINI:
        return perguntar_gemini(prompt, system_instruction=system_msg)
    else:
        return "Motor Gemini selecionado, mas 'gemini_engine.py' não encontrado ou Key ausente."

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("⚙️ Nexus Core")
st.session_state.motor_ia = st.sidebar.selectbox("Cérebro Ativo:", ["Groq", "Gemini"])
if not HAS_GEMINI and st.session_state.motor_ia == "Gemini":
    st.sidebar.warning("Arquivo gemini_engine.py não detectado.")

tabs = st.tabs(["🔎 Scanner 30x", "⚔️ Arsenal 10x", "🔥 Radar & Termômetro", "🎥 Estúdio IA", "💰 Financeiro"])

# --- ABA 0: SCANNER (IGUAL AO APP 8) ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências High-Ticket")
    c1, c2 = st.columns([3, 1])
    nicho = c1.text_input("Nicho alvo:", value="Utilidades Domésticas")
    
    if st.button("🚀 Iniciar Mineração Massiva", use_container_width=True):
        with st.status("Minerando dados..."):
            p = f"Liste 30 produtos de {nicho} na Shopee BR. Formato EXATO: NOME: [nome] | CALOR: [0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"
            st.session_state.res_busca = gerar_ia(p, "Responda apenas a lista, sem introdução.")
            st.rerun()

    if st.session_state.res_busca:
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha and "NOME:" in linha:
                try:
                    parts = linha.split("|")
                    nome = parts[0].split("NOME:")[1].strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    valor = parts[2].split("VALOR:")[1].strip()
                    cresc = parts[3].split("CRESC:")[1].strip()
                    link_orig = parts[4].split("URL:")[1].strip()
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"📦 **{nome}**")
                            st.caption(f"💰 {valor} | 📈 {cresc}")
                        with col2:
                            st.progress(min(calor/100, 1.0))
                            st.write(f"🌡️ {calor}°C")
                        with col3:
                            if st.button("Selecionar", key=f"sel_{idx}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link_orig
                                st.toast(f"✅ {nome} carregado!")
                except: continue

# --- ABA 1: ARSENAL (10 VARIAÇÕES) ---
with tabs[1]:
    st.header("⚔️ Arsenal de Escala 10x")
    if st.session_state.sel_nome:
        st.success(f"🎯 Alvo Ativo: {st.session_state.sel_nome}")
        if st.button("🔥 DISPARAR 10 VARIAÇÕES VIRAIS"):
            with st.spinner("Gerando Munição..."):
                p_ars = f"Crie 10 roteiros curtos (15s) para TikTok do produto {st.session_state.sel_nome}. Separe cada um com ###"
                res_ars = gerar_ia(p_ars)
                for i, v in enumerate(res_ars.split("###")):
                    if len(v) > 10:
                        with st.container(border=True):
                            st.subheader(f"Variação V{i+1}")
                            st.write(v)
                            if st.button(f"Usar V{i+1}", key=f"u_{i}"):
                                st.session_state.copy_ativa = v
                                st.toast("Roteiro enviado ao Estúdio!")
    else: st.warning("Selecione um produto no Scanner.")

# --- ABA 2: RADAR & TERMÔMETRO (RECUPERADO) ---
with tabs[2]:
    st.header("🌍 Inteligência Global")
    c_eua, c_br = st.columns(2)
    with c_eua:
        st.subheader("🇺🇸 Radar USA")
        if st.button("🔍 Escanear TikTok USA"):
            res = gerar_ia("Liste 5 produtos virais nos EUA hoje para dropshipping.")
            st.info(res)
    with c_br:
        st.subheader("🇧🇷 Termômetro Shopee BR")
        if st.button("🔥 Trends Brasil"):
            res = gerar_ia("Quais os 5 termos mais buscados na Shopee Brasil agora?")
            st.success(res)

# --- ABA 3: ESTÚDIO (CONECTADO AO WEBHOOK) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia IA")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    copy_f = st.text_area("Roteiro:", value=st.session_state.copy_ativa, height=150)
    
    if st.button("🚀 Produzir Mídia Completa"):
        webhook = st.secrets.get("WEBHOOK_POST_URL")
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        if webhook:
            link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
            requests.post(webhook, json={"prod": prod_f, "copy": copy_f, "link": link_final})
            st.success("✅ Enviado para Make.com!")
