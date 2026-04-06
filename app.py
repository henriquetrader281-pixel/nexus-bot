import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- 1. CONEXÃO MODULAR (Tenta importar, mas não quebra se faltar) ---
try:
    import gemini_engine as gemini
    import producao_midia as midia
    import agendador as agenda
    import radar_engine as radar
    MODULOS_OK = True
except ImportError:
    MODULOS_OK = False

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Absolute V100", layout="wide", page_icon="🔱")

# --- 3. DATABASE DE PERFORMANCE (Recuperado das V22-V27) ---
DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=[
        "data", "produto", "status", "views", "cliques", "vendas", "faturamento", "copy"
    ]).to_csv(DATA_PATH, index=False)

# --- 4. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Senha:", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- 5. MOTORES DE IA & UTILITÁRIOS ---
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "copy_ativa" not in st.session_state: st.session_state.copy_ativa = ""

def gerar_ia(prompt, system_msg="Seja direto e focado em conversão."):
    if st.session_state.get("motor_ia") == "Gemini" and MODULOS_OK:
        return gemini.perguntar_gemini(prompt, system_instruction=system_msg)
    else:
        res = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content": system_msg}, {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content

# --- 6. INTERFACE PRINCIPAL ---
st.sidebar.title("⚙️ Nexus Core")
st.session_state.motor_ia = st.sidebar.selectbox("Cérebro Ativo:", ["Groq", "Gemini"])

tabs = st.tabs(["🔎 Scanner", "⚔️ Arsenal 10x", "🔥 Radar", "🎥 Estúdio", "📊 Performance"])

# --- ABA 0: SCANNER (Com Visual de Calor e Link) ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências")
    nicho = st.text_input("Nicho alvo:", value="Cozinha")
    if st.button("🚀 Minerar Produtos", use_container_width=True):
        p = f"Liste 30 produtos de {nicho}. Formato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"
        st.session_state.res_busca = gerar_ia(p, "Apenas a lista crua.")
        st.rerun()

    if st.session_state.res_busca:
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha and "NOME:" in linha:
                try:
                    parts = linha.split("|")
                    nome = parts[0].split(":")[1].strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    link_orig = parts[4].split("URL:")[1].strip()
                    
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 1])
                        c1.write(f"📦 **{nome}**")
                        c2.progress(min(calor/100, 1.0))
                        c2.write(f"🌡️ {calor}°C")
                        if c3.button("Selecionar", key=f"s_{idx}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link_orig
                            st.toast("Produto capturado!")
                except: continue

# --- ABA 1: ARSENAL (Gerador de 10 Variações) ---
with tabs[1]:
    if st.session_state.sel_nome:
        st.success(f"🎯 Alvo: {st.session_state.sel_nome}")
        if st.button("🔥 GERAR 10 ROTEIROS VIRAIS"):
            res = gerar_ia(f"Crie 10 roteiros TikTok para {st.session_state.sel_nome}. Separe com ###")
            for i, v in enumerate(res.split("###")):
                with st.container(border=True):
                    st.write(v)
                    if st.button(f"Usar V{i+1}", key=f"u_{i}"):
                        st.session_state.copy_ativa = v

# --- ABA 2: RADAR & TERMÔMETRO (Recuperado) ---
with tabs[2]:
    st.header("🌍 Radar de Inteligência")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔍 Trends USA"):
            if MODULOS_OK: st.info(radar.obter_trends_globais("EUA"))
            else: st.info(gerar_ia("5 produtos virais nos EUA agora."))
    with c2:
        if st.button("🔥 Trends Brasil"):
            if MODULOS_OK: st.success(radar.obter_trends_globais("BR"))
            else: st.success(gerar_ia("5 termos mais buscados na Shopee BR."))

# --- ABA 3: ESTÚDIO (Com Gerador de Deep Link) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    copy_f = st.text_area("Roteiro:", value=st.session_state.copy_ativa)
    
    if st.button("🚀 Produzir e Gerar Deep Link"):
        # Lógica de Deep Link recuperada
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_deep = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
        
        if MODULOS_OK:
            msg = midia.gerar_video_ia(prod_f, copy_f, link_deep)
            st.success(msg)
        else:
            # Webhook direto se o módulo não existir
            webhook = st.secrets.get("WEBHOOK_POST_URL")
            requests.post(webhook, json={"prod": prod_f, "copy": copy_f, "link": link_deep})
            st.success("Enviado via Webhook Direto!")

# --- ABA 4: PERFORMANCE (O agendador agora salva aqui) ---
with tabs[4]:
    st.header("📊 Painel de Performance")
    df = pd.read_csv(DATA_PATH)
    st.dataframe(df, use_container_width=True)
    if st.button("Clear Data"):
        pd.DataFrame(columns=df.columns).to_csv(DATA_PATH, index=False)
        st.rerun()
