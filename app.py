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
    import radar_engine as radar
    MODULOS_OK = True
except ImportError:
    MODULOS_OK = False

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Absolute V100", layout="wide", page_icon="🔱")

# --- 3. DATABASE ---
DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data", "produto", "status", "views", "cliques", "vendas", "faturamento", "copy", "link"]).to_csv(DATA_PATH, index=False)

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

# --- 5. MOTORES DE IA ---
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

for key in ["res_busca", "sel_nome", "sel_link", "copy_ativa"]:
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

# --- 6. INTERFACE PRINCIPAL ---
st.sidebar.title("⚙️ Nexus Core")
st.session_state.motor_ia = st.sidebar.selectbox("Cérebro Ativo:", ["Groq", "Gemini"])

tabs = st.tabs(["🔎 Scanner", "⚔️ Arsenal 10x", "🔥 Radar", "🎥 Estúdio", "📊 Performance"])

# --- ABA 0: SCANNER CORRIGIDO ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências")
    nicho = st.text_input("Nicho alvo:", value="Cozinha")
    if st.button("🚀 Minerar Produtos", use_container_width=True):
        p = f"Liste 30 produtos de {nicho}. Formato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"
        st.session_state.res_busca = gerar_ia(p, "Retorne APENAS a lista crua separada por pipes.")
        st.rerun()

    if st.session_state.res_busca:
        # Linha de Correção ativa
        limpo = st.session_state.res_busca.replace("**", "").replace("Aqui está", "").strip()
        linhas = [l.strip() for l in limpo.split('\n') if "|" in l]
        
        if not linhas:
            st.warning("⚠️ O formato da IA desalinhou. Execute o script correcao.py ou tente outro nicho.")
        
        for idx, linha in enumerate(linhas):
            try:
                parts = [p.strip() for p in linha.split("|")]
                nome = parts[0].split("NOME:")[1].strip() if "NOME:" in parts[0] else parts[0]
                calor = int(''.join(filter(str.isdigit, parts[1])))
                link_orig = parts[4].split("URL:")[1].strip() if "URL:" in parts[4] else "https://shopee.com.br"
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.write(f"📦 **{nome}**")
                    c2.progress(min(calor/100, 1.0))
                    c2.write(f"🌡️ {calor}°C")
                    if c3.button("Selecionar", key=f"s_{idx}"):
                        st.session_state.sel_nome = nome
                        st.session_state.sel_link = link_orig
                        st.toast(f"✅ {nome} capturado!")
            except:
                continue

# --- ABA 1: ARSENAL ---
with tabs[1]:
    if st.session_state.sel_nome:
        st.success(f"🎯 Alvo: {st.session_state.sel_nome}")
        if st.button("🔥 GERAR 10 ROTEIROS VIRAIS"):
            res = gerar_ia(f"Crie 10 roteiros TikTok para {st.session_state.sel_nome}. Separe com ###")
            for i, v in enumerate(res.split("###")):
                if len(v) > 10:
                    with st.container(border=True):
                        st.write(v)
                        if st.button(f"Usar V{i+1}", key=f"u_{i}"):
                            st.session_state.copy_ativa = v
                            st.toast("Roteiro enviado ao Estúdio!")

# --- ABA 3: ESTÚDIO & AGENDADOR ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    copy_f = st.text_area("Roteiro:", value=st.session_state.copy_ativa, height=150)
    
    if st.button("🚀 Agendar e Produzir"):
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_deep = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
        
        if MODULOS_OK:
            status = agenda.salvar_na_fila(prod_f, copy_f, link_deep)
            st.success(status)
            midia.gerar_video_ia(prod_f, copy_f)
        else:
            st.warning("Módulos offline. Enviando via Webhook...")
            webhook = st.secrets.get("WEBHOOK_POST_URL")
            if webhook:
                requests.post(webhook, json={"prod": prod_f, "copy": copy_f, "link": link_deep})
                st.success("Enviado ao Webhook com sucesso!")
            else:
                st.error("Webhook não configurado nos secrets.")

# --- ABA 4: PERFORMANCE ---
with tabs[4]:
    st.header("📊 Painel de Performance")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        st.dataframe(df, use_container_width=True)
