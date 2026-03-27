import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd

# --- 1. SETUP & SEGURANÇA (Patches 01-10) ---
st.set_page_config(page_title="Nexus Ultra: Final Master", page_icon="🔱", layout="wide")

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

# --- 2. MOTORES IA & AFILIADOS (Patches 14 & 20) ---
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

# --- 3. AUTO-REFRESH (Patch 13) ---
hoje = datetime.now().strftime('%d/%m/%Y')
if "ultima_mineracao_data" not in st.session_state: st.session_state["ultima_mineracao_data"] = None

# --- 4. INTERFACE (Patches 11-22) ---
st.title("🔱 Nexus Ultra: Central de Vendas Autônoma")
st.caption(f"Operador: {st.session_state['user_email']} | Data: {hoje} | Status: Conectado")

tabs = st.tabs(["🔎 Mineração & Links", "📈 SEO & Sourcing", "🎥 Criativos & Voz IA", "🚀 Postagem (FB/IG/TK)", "📊 Exportar"])

# --- TAB 1: MINERAÇÃO & DEEPLINK (Patch 13 & 20) ---
with tabs[0]:
    st.header("🎯 Descoberta de Produtos Virais")
    col_n, col_p = st.columns(2)
    nicho = col_n.selectbox("Nicho:", ["Cozinha Criativa", "Saúde & Beleza", "Tech/Eletrônicos", "Pet Shop", "Ferramentas"])
    lista_precos = [0, 20, 40, 60, 80, 100, 150, 200, 500]
    preco_min, preco_max = col_p.select_slider("Preço:", options=lista_precos, value=(40, 100))

    if st.button("🔄 Executar Varredura Inteligente", use_container_width=True) or st.session_state["ultima_mineracao_data"] != hoje:
        with st.status("Minerando tendências 2026..."):
            res = gerar_ia(f"Filtre 10 produtos 🚀 em {nicho} (R${preco_min}-{preco_max}). Tabela Markdown: Produto, Status Google (🚀, 📈, ⚠️), Link Shopee Original.")
            st.session_state['tabela_minerada'] = res
            st.session_state['ultima_mineracao_data'] = hoje
            st.toast("Nexus atualizado para hoje!")

    if 'tabela_minerada' in st.session_state:
        st.markdown(st.session_state['tabela_minerada'])
        st.divider()
        st.subheader("🔗 Gerador de Link de Afiliado")
        link_origem = st.text_input("Cole o Link Shopee aqui:")
        if link_origem:
            link_pronto = converter_afiliado(link_origem)
            st.success(f"Link Afiliado: {link_pronto}")
            st.session_state['ultimo_link_aff'] = link_pronto

# --- TAB 2: SEO & SOURCING (Patch 14) ---
with tabs[1]:
    st.header("📈 Estratégia de SEO & Palavras-Passe")
    if st.button("Analisar Buscas Google 2026"):
        st.write(gerar_ia(f"Top 5 Palavras-Passe e 3 títulos de anúncios para {nicho} no Google Brasil hoje."))

# --- TAB 3: CRIATIVOS & VOZ (Patch 19 & 17) ---
with tabs[2]:
    st.header("🎥 Estúdio de Criativos Viral")
    p_ativo = st.text_input("Produto alvo do anúncio:", placeholder="Ex: Mini Selador a Vácuo")
    if p_ativo:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔗 Referências")
            st.link_button("🔥 TikTok (+Views)", f"https://www.tiktok.com/search/video?q={urllib.parse.quote(p_ativo)}")
            st.link_button("📺 Shorts (+Views)", f"https://www.youtube.com/results?search_query={urllib.parse.quote(p_ativo)}&sp=CAM%253D")
        with c2:
            st.subheader("🎙️ Narração & Roteiro")
            if st.button("🎙️ Gerar Voz IA + Roteiro"):
                script = gerar_ia(f"Crie um roteiro de 15s para {p_ativo}. Use [LOCUÇÃO] para o áudio e [CENA] para o visual. Inclua música viral.")
                st.session_state['script_final'] = script
        
        if 'script_final' in st.session_state:
            st.markdown(st.session_state['script_final'])

# --- TAB 4: POSTAGEM (Patch 15, 21 & 22) ---
with tabs[3]:
    st.header("🚀 Automação de Postagem (Facebook Pilot)")
    destinos = st.multiselect("Postar em:", ["Facebook Reels", "Grupos FB (Achadinhos)", "Instagram Reels", "TikTok"], default=["Facebook Reels", "Grupos FB (Achadinhos)"])
    
    if st.button("🔥 DISPARAR PARA FILA (AUTO-POST)", use_container_width=True):
        webhook = st.secrets.get("WEBHOOK_POST_URL")
        if webhook:
            payload = {
                "produto": p_ativo,
                "link": st.session_state.get('ultimo_link_aff'),
                "copy": st.session_state.get('script_final'),
                "canais": destinos,
                "data": hoje
            }
            try:
                requests.post(webhook, json=payload)
                st.balloons()
                st.success("✅ Nexus enviou os dados para o Make.com! Postagem agendada nos horários de pico.")
            except: st.error("Erro na conexão com o Webhook.")
        else: st.warning("Configure o WEBHOOK_POST_URL para postar sozinho.")

# --- TAB 5: EXPORTAR (Patch 16) ---
with tabs[4]:
    st.header("📊 Exportação de Dados")
    if 'tabela_minerada' in st.session_state:
        st.download_button("📥 Baixar Relatório Diário (TXT)", st.session_state['tabela_minerada'], file_name=f"nexus_{hoje}.txt")
    else: st.warning("Sem dados para exportar.")
