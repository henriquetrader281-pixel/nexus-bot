import streamlit as st
from groq import Groq
import urllib.parse
import requests

# --- 1. CONEXÃO MODULAR (IMPORTAÇÃO DOS SEUS .PY) ---
try:
    import gemini_engine as gemini   
    import producao_midia as midia  
    import agendador as agenda      
    import radar_engine as radar    
    MODULOS_OK = True
except ImportError as e:
    MODULOS_OK = False
    ERRO_IMPORT = str(e)

# --- 2. CONFIGURAÇÃO E LOGIN ---
st.set_page_config(page_title="Nexus Absolute V100", layout="wide", page_icon="🔱")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔱 Nexus Login")
        senha = st.text_input("Senha:", type="password")
        if st.button("Acessar Nexus", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

# --- 3. MOTORES DE IA ---
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""

def gerar_ia(prompt, system_msg="Direto e técnico."):
    if st.session_state.get("motor_ia") == "Gemini" and MODULOS_OK:
        return gemini.perguntar_gemini(prompt, system_instruction=system_msg)
    else:
        res = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content": system_msg}, {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content

# --- 4. INTERFACE ---
st.sidebar.title("⚙️ Nexus Core")
st.session_state.motor_ia = st.sidebar.selectbox("Cérebro Ativo:", ["Groq", "Gemini"])
if not MODULOS_OK: st.sidebar.error(f"⚠️ Faltando: {ERRO_IMPORT}")

tabs = st.tabs(["🔎 Scanner", "⚔️ Arsenal 10x", "🔥 Radar", "🎥 Estúdio", "📅 Agendador"])

# --- SCANNER (CORRIGIDO PARA NÃO TRAVAR) ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências")
    nicho = st.text_input("Nicho alvo:", value="Cozinha Criativa")
    if st.button("🚀 Iniciar Mineração Massiva", use_container_width=True):
        with st.status("Minerando..."):
            p = f"Liste 30 produtos de {nicho}. Formato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"
            st.session_state.res_busca = gerar_ia(p, "Retorne APENAS a lista no formato solicitado.")
            st.rerun()

    if st.session_state.res_busca:
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha and "NOME:" in linha:
                try:
                    # Limpeza de dados para evitar "pau" na exibição
                    parts = linha.split("|")
                    nome = parts[0].split(":")[1].strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    valor = parts[2].split(":")[1].strip()
                    
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 1])
                        c1.write(f"📦 **{nome}**")
                        c1.caption(f"💰 {valor}")
                        c2.progress(min(calor/100, 1.0))
                        c2.write(f"🌡️ {calor}°C")
                        if c3.button("Selecionar", key=f"s_{idx}"):
                            st.session_state.sel_nome = nome
                            st.toast(f"{nome} selecionado!")
                except: continue

# --- ARSENAL (10 VARIAÇÕES) ---
with tabs[1]:
    if st.session_state.sel_nome:
        st.success(f"🎯 Alvo: {st.session_state.sel_nome}")
        if st.button("🔥 DISPARAR 10 VARIAÇÕES"):
            res = gerar_ia(f"Crie 10 roteiros TikTok para {st.session_state.sel_nome}. Separe com ###")
            for i, v in enumerate(res.split("###")):
                with st.container(border=True):
                    st.write(v)
                    if st.button(f"Usar V{i+1}", key=f"u_{i}"):
                        st.session_state.copy_ativa = v

# --- MODULOS EXTERNOS (CHAMADAS) ---
with tabs[2]:
    if st.button("🔍 Radar Global"):
        if MODULOS_OK: st.write(radar.obter_trends_globais())

with tabs[3]:
    if st.button("🎬 Produzir Mídia"):
        if MODULOS_OK: st.success(midia.gerar_video_ia(st.session_state.sel_nome))

with tabs[4]:
    if st.button("🗓️ Agendar Post"):
        if MODULOS_OK: st.success(agenda.agendar_no_buffer(st.session_state.sel_nome))
