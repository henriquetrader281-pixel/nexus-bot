import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- 1. CONEXÃO MODULAR ---
try:
    import gemini_engine as gemini
    import producao_midia as midia
    import agendador as agenda
    MODULOS_OK = True
except ImportError:
    MODULOS_OK = False

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Absolute V100", layout="wide", page_icon="🔱")

# --- 3. DATABASE ---
DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=[
        "data", "produto", "valor", "ticket", "marketplace", "status", "views", "cliques", "vendas", "faturamento", "copy", "link"
    ]).to_csv(DATA_PATH, index=False)

# --- 4. LOGIN ---
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

# --- 5. MOTORES DE IA ---
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

for key in ["res_busca", "sel_nome", "sel_link", "copy_ativa", "sel_valor", "sel_ticket"]:
    if key not in st.session_state: st.session_state[key] = ""

def gerar_ia(prompt, system_msg="Seja direto e focado em conversão."):
    if st.session_state.get("motor_ia") == "Gemini" and MODULOS_OK:
        return gemini.perguntar_gemini(prompt, system_instruction=system_msg)
    else:
        res = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content": system_msg}, {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content

# --- 6. SIDEBAR (CONFIGURAÇÃO DE BUSCA) ---
st.sidebar.title("⚙️ Nexus Core")
st.session_state.motor_ia = st.sidebar.selectbox("Cérebro Ativo:", ["Groq", "Gemini"])

# NOVO: SELETOR DE MARKETPLACE
mkt_alvo = st.sidebar.radio(
    "🎯 Marketplace Alvo:",
    ["Shopee", "Mercado Livre", "Amazon"],
    index=0 # Inicialmente Shopee
)

tabs = st.tabs(["🔎 Scanner", "⚔️ Arsenal 10x", "🔥 Radar", "🎥 Estúdio", "📊 Performance"])

# --- ABA 0: SCANNER DIRECIONADO ---
with tabs[0]:
    st.header(f"🔎 Scanner de Tendências ({mkt_alvo})")
    nicho = st.text_input("Nicho alvo:", value="Cozinha")
    
    if st.button(f"🚀 Minerar na {mkt_alvo}", use_container_width=True):
        # Prompt agora inclui o Marketplace selecionado para busca direcionada
        p = f"Liste 20 produtos virais de {nicho} que estão vendendo muito na {mkt_alvo} Brasil. " \
            f"Formato exato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | TICKET: [Baixo/Médio/Alto] | URL: [link real ou simulado da {mkt_alvo}]"
        
        st.session_state.res_busca = gerar_ia(p, f"Você é um analista de tendências especialista em {mkt_alvo}. Retorne apenas a lista.")
        st.rerun()

    if st.session_state.res_busca:
        limpo = st.session_state.res_busca.replace("**", "").strip()
        linhas = [l.strip() for l in limpo.split('\n') if "|" in l]
        
        for idx, linha in enumerate(linhas):
            try:
                parts = [p.strip() for p in linha.split("|")]
                nome = parts[0].split("NOME:")[1].strip() if "NOME:" in parts[0] else parts[0]
                calor = int(''.join(filter(str.isdigit, parts[1])))
                valor = parts[2].split("VALOR:")[1].strip() if "VALOR:" in parts[2] else parts[2]
                ticket = parts[3].split("TICKET:")[1].strip() if "TICKET:" in parts[3] else "Médio"
                link_orig = parts[4].split("URL:")[1].strip() if "URL:" in parts[4] else "#"
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.write(f"📦 **{nome}**")
                        st.caption(f"💰 {valor} | 🏷️ {ticket} | 🏢 {mkt_alvo}")
                    with c2:
                        st.progress(min(calor/100, 1.0))
                        st.write(f"🌡️ {calor}°C")
                    with c3:
                        if st.button("Selecionar", key=f"s_{idx}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link_orig
                            st.session_state.sel_valor = valor
                            st.session_state.sel_ticket = ticket
                            st.session_state.sel_mkt = mkt_alvo
                            st.toast(f"✅ Capturado da {mkt_alvo}!")
            except: continue

# --- ABA 3: ESTÚDIO (AGENDAMENTO COM MKT) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    
    if st.button("🚀 Agendar e Produzir"):
        # Lógica de Deep Link baseada no Marketplace
        if st.session_state.get("sel_mkt") == "Shopee":
            aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
            link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
        else:
            # Para Amazon/ML, usa o link direto ou seu encurtador
            link_final = st.session_state.sel_link

        if MODULOS_OK:
            status = agenda.salvar_na_fila(prod_f, st.session_state.copy_ativa, link_final, st.session_state.sel_valor, st.session_state.sel_mkt)
            st.success(status)
            midia.gerar_video_ia(prod_f, st.session_state.copy_ativa)
