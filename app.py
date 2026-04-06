import streamlit as st
from groq import Groq
import urllib.parse
import requests

# --- 1. CONEXÃO COM MÓDULOS EXTERNOS (.py) ---
try:
    import gemini_engine as gemini   # Programação e IA Avançada
    import producao_midia as midia  # Geração de Vídeo e Imagem
    import agendador as agenda      # Automação de Postagens
    import radar_engine as radar    # Monitoramento Global
    MODULOS_OK = True
except ImportError as e:
    MODULOS_OK = False
    ERRO_DETALHADO = str(e)

# --- 2. CONFIGURAÇÃO E LOGIN SEGURO ---
st.set_page_config(page_title="Nexus Absolute V100", layout="wide", page_icon="🔱")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Senha de Acesso:", type="password")
        if st.button("Acessar Nexus", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
    st.stop()

# --- 3. INICIALIZAÇÃO DE MOTORES ---
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "copy_ativa" not in st.session_state: st.session_state.copy_ativa = ""

# --- 4. FUNÇÃO DE IA ORQUESTRADORA ---
def gerar_ia(prompt, system_msg="Seja direto."):
    if st.session_state.motor_ia == "Gemini" and MODULOS_OK:
        return gemini.perguntar_gemini(prompt, system_instruction=system_msg)
    else:
        res = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content": system_msg}, {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content

# --- 5. INTERFACE (SIDEBAR & TABS) ---
st.sidebar.title("🔱 Nexus Core")
st.session_state.motor_ia = st.sidebar.selectbox("Cérebro Ativo:", ["Groq", "Gemini"])
if not MODULOS_OK: st.sidebar.error(f"Erro: Arquivo {ERRO_DETALHADO} faltando!")

tabs = st.tabs(["🔎 Scanner", "⚔️ Arsenal 10x", "🔥 Radar", "🎥 Estúdio", "📅 Agendador"])

# --- SCANNER ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências")
    nicho = st.text_input("Nicho alvo:", value="Utilidades")
    if st.button("🚀 Iniciar Mineração Massiva", use_container_width=True):
        p = f"Liste 30 produtos de {nicho}. Formato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"
        st.session_state.res_busca = gerar_ia(p, "Apenas lista crua.")
        st.rerun()

    if st.session_state.res_busca:
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha:
                try:
                    parts = linha.split("|")
                    nome = parts[0].split(":")[1].strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 1])
                        c1.write(f"📦 **{nome}**")
                        c2.progress(min(calor/100, 1.0))
                        if c3.button("Selecionar", key=f"s_{idx}"):
                            st.session_state.sel_nome = nome
                            st.toast(f"{nome} selecionado!")
                except: continue

# --- ARSENAL ---
with tabs[1]:
    if st.session_state.sel_nome:
        if st.button("🔥 DISPARAR 10 VARIAÇÕES"):
            res = gerar_ia(f"10 roteiros TikTok para {st.session_state.sel_nome}. Separe com ###")
            for i, v in enumerate(res.split("###")):
                with st.container(border=True):
                    st.write(v)
                    if st.button(f"Usar V{i+1}", key=f"u_{i}"):
                        st.session_state.copy_ativa = v

# --- RADAR (CHAMA radar_engine.py) ---
with tabs[2]:
    st.header("🌍 Inteligência Global")
    if st.button("🔍 Escanear Tendências USA/BR"):
        if MODULOS_OK:
            dados = radar.obter_trends_globais(st.session_state.motor_ia)
            st.write(dados)
        else: st.error("Módulo Radar ausente.")

# --- ESTÚDIO (CHAMA producao_midia.py) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    if st.button("🎬 Produzir Criativo Completo"):
        if MODULOS_OK:
            status = midia.gerar_workflow_midia(st.session_state.sel_nome, st.session_state.copy_ativa)
            st.success(status)
        else: st.error("Módulo Produção ausente.")

# --- AGENDADOR (CHAMA agendador.py) ---
with tabs[4]:
    st.header("📅 Agendador Social")
    if st.button("🗓️ Enviar para Fila de Postagem"):
        if MODULOS_OK:
            status = agenda.executar_agendamento(st.session_state.sel_nome, st.session_state.copy_ativa)
            st.success(status)
        else: st.error("Módulo Agendador ausente.")
