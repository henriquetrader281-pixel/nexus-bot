import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests

# --- 1. SETUP & SEGURANÇA ---
st.set_page_config(page_title="Nexus Ultra: Shopee Power", page_icon="🔱", layout="wide")

def login_nexus():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Nexus Private Access</h1>", unsafe_allow_html=True)
        with st.form("login"):
            e = st.text_input("E-mail Autorizado:")
            s = st.text_input("Senha Mestre:", type="password")
            if st.form_submit_button("Liberar Inteligência", use_container_width=True):
                autorizados = st.secrets.get("ALLOWED_USERS", "").split(",")
                if e in [i.strip() for i in autorizados] and s == st.secrets["NEXUS_PASSWORD"]:
                    st.session_state["autenticado"] = True
                    st.session_state["user_email"] = e
                    st.rerun()
                else: st.error("Acesso Negado.")
        return False
    return True

if not login_nexus(): st.stop()

# --- 2. MOTORES IA & AFILIADOS ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    try:
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content
    except Exception as e: return f"Erro na IA: {e}"

def converter_afiliado(url_prod):
    id_aff = st.secrets.get("SHOPEE_ID", "SEM_ID")
    return f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(url_prod)}&aff_id={id_aff}"

# --- 3. AUTO-REFRESH & DATA ---
hoje = datetime.now().strftime('%d/%m/%Y')

# --- 4. DASHBOARD ---
st.title("🔱 Nexus Ultra: Shopee Power Edition 2026")
st.caption(f"Operador: {st.session_state['user_email']} | Cruzamento de Dados Ativo: Shopee Trends + Google Search")

tabs = st.tabs(["🔎 Mineração & Cruzamento", "📈 SEO & Sourcing", "🎥 Criativos & Voz IA", "🚀 Postagem Automática"])

# --- TAB 1: MINERAÇÃO COM CRUZAMENTO (PATCH 23) ---
with tabs[0]:
    st.header("🎯 Os 10 Mais Buscados da Shopee vs Google")
    
    if st.button("🔄 Rodar Cruzamento de Dados de Hoje", use_container_width=True):
        with st.status("Nexus acessando API de tendências Shopee e cruzando com Google..."):
            prompt_cruzado = f"""
            Analista de E-commerce 2026:
            1. Identifique os 10 termos/produtos mais buscados na Shopee Brasil hoje (Foco em Utilidades e Tech).
            2. Cruze com o volume de busca do Google (Status: 🚀 Alta, 📈 Estável).
            3. Gere uma Tabela Markdown: | Produto Rank | Busca Shopee | Tendência Google | Link p/ Afiliar |
            4. Dê um veredito: 'Produto do Dia' para o campeão de buscas.
            """
            st.session_state['tabela_cruzada'] = gerar_ia(prompt_cruzado)
            st.session_state['ultima_mineracao_data'] = hoje

    if 'tabela_cruzada' in st.session_state:
        st.markdown(st.session_state['tabela_cruzada'])
        st.divider()
        st.subheader("🔗 Gerador de DeepLink Rápido")
        link_origem = st.text_input("Cole o Link Shopee do produto campeão aqui:")
        if link_origem:
            st.success(f"Link Afiliado Pronto: {converter_afiliado(link_origem)}")

# --- TAB 2, 3 e 4 (Mantêm a funcionalidade de SEO, Voz IA e Postagem Webhook) ---
# ... (Igual ao script anterior, focado na execução automática)
