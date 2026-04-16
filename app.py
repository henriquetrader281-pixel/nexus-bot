import streamlit as st
import arsenal, trends, update, radar_engine, estudio, postador
import pandas as pd
import os
import urllib.parse
from datetime import datetime
import mineracao as miny
import google.generativeai as genai
import json

st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

def get_nexus_intelligence():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"Analise tendências de HOJE ({hoje}) no TikTok Brasil e Reels. Retorne APENAS JSON: {{\"trends\": [{{\"musica\": \"nome\", \"score\": 95, \"razao\": \"...\", \"aida_hook\": \"...\"}}]}}"
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"trends": [{"musica": "Brazilian Funk Instrumental", "score": 98, "razao": "Alta conversão", "aida_hook": "SÓ 17 REAIS? 😱"}]}

def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            n_exibir = nome.replace("*", "").strip() if nome else "Produto Detectado"
            st.markdown(f"**{ico} {n_exibir}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        with c2:
            try:
                c_string = "".join(filter(str.isdigit, str(calor)))
                calor_num = min(max(int(c_string), 0), 100) if c_string else 0
            except: calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", use_container_width=True):
            st.session_state.sel_nome = n_exibir
            st.session_state.sel_link = link
            st.session_state.sel_preco = valor
            update.registrar_mineracao(n_exibir, link, calor_num)
            st.toast(f"Selecionado: {n_exibir}")

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    senha = st.text_input("Acesso:", type="password")
    if st.button("AUTENTICAR", use_container_width=True):
        if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')

st.sidebar.title("🔱 Nexus Control")
mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])
st.session_state.mkt_global = mkt_global

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD"])

with tabs[0]:
    col_s1, col_s2 = st.columns([1, 2])
    qtd = col_s1.selectbox("Volume:", [15, 30, 45], index=0)
    foco_nicho = col_s2.text_input("🎯 Nicho:", value="Cozinha Criativa", key="foco_nicho")

    if st.button("🔥 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando com Groq..."):
            prompt = f"Não escreva introdução. Liste {qtd} produtos de {mkt_global} para '{foco_nicho}'. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt, mkt_global, "groq")

    if st.session_state.res_busca:
        st.divider()
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha:
                try:
                    partes = [p.strip() for p in linha.split('|')]
                    dados = {p.split(':')[0].strip().upper(): p.split(':')[1].strip() for p in partes if ':' in p}
                    n_f = dados.get("NOME") or partes[0].replace("*", "").split(':')[-1].strip()
                    renderizar_card_produto(idx, n_f, dados.get("VALOR", "---"), dados.get("CALOR", "0"), "Médio", dados.get("URL", "#"), mkt_global)
                except: continue

with tabs[1]: arsenal.exibir_arsenal(miny, "groq")
with tabs[2]: trends.exibir_trends()
with tabs[3]: estudio.exibir_estudio(miny, "groq")
with tabs[4]: postador.exibir_postador(miny, "groq")
with tabs[5]: update.dashboard_performance_simples()
