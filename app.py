import streamlit as st
import arsenal, trends, update, radar_engine, estudio, postador
import mineracao as miny
import google.generativeai as genai
import json, os, urllib.parse
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

def get_nexus_intelligence():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"Trends HOJE {hoje} TikTok/Reels Brasil. Retorne JSON: {{\"trends\": [{{\"musica\": \"nome\", \"score\": 95, \"razao\": \"...\", \"aida_hook\": \"...\"}}]}}"
        res = model.generate_content(prompt)
        clean = res.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except:
        return {"trends": [{"musica": "Brazilian Funk Instrumental", "score": 98, "razao": "Alta conversão", "aida_hook": "SÓ 17 REAIS? 😱"}]}

def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"**{icones.get(mkt, '🛍️')} {nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        with c2:
            c_num = "".join(filter(str.isdigit, str(calor)))
            c_f = min(max(int(c_num), 0), 100) if c_num else 0
            st.progress(c_f / 100)
            st.write(f"🌡️ {c_f}°C")
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt}", use_container_width=True):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.session_state.sel_preco = valor
            update.registrar_mineracao(nome, link, c_f)
            st.toast(f"Alvo: {nome}")

# --- 2. LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus</h1>", unsafe_allow_html=True)
    senha = st.text_input("Acesso:", type="password")
    if st.button("ENTRAR", use_container_width=True):
        if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# --- 3. INTERFACE ---
st.sidebar.title("🔱 Nexus Control")
mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt_global

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

with tabs[0]:
    col1, col2 = st.columns([1, 2])
    qtd = col1.selectbox("Qtd:", [15, 30, 45], index=0)
    nicho = col2.text_input("🎯 Nicho:", value="Cozinha Criativa", key="foco_nicho")
    
    if st.button("🔥 INICIAR VARREDURA", use_container_width=True):
        prompt = f"Sem introdução. Liste {qtd} produtos de {mkt_global} para '{nicho}'. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo] | URL: [link]"
        st.session_state.res_busca = miny.minerar_produtos(prompt, mkt_global, "groq")
    
    if st.session_state.get("res_busca"):
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha:
                partes = [p.strip() for p in linha.split('|')]
                d = {p.split(':')[0].strip().upper(): p.split(':')[1].strip() for p in partes if ':' in p}
                # Lógica Blindada de Nome
                n_f = d.get("NOME") or partes[0].replace("*", "").split(':')[-1].strip()
                v_f = d.get("VALOR", "---")
                c_f = d.get("CALOR", "0")
                renderizar_card_produto(idx, n_f, v_f, c_f, "Médio", d.get("URL", "#"), mkt_global)

with tabs[1]: arsenal.exibir_arsenal(miny, "groq")
with tabs[2]: trends.exibir_trends()
with tabs[3]: estudio.exibir_estudio(miny, "groq")
with tabs[4]: postador.exibir_postador(miny, "groq")
with tabs[5]: update.dashboard_performance_simples()
