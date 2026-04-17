import streamlit as st
import arsenal
import trends
import pandas as pd
import update
import radar_engine
import os
import urllib.parse
from datetime import datetime
import mineracao as miny
import estudio  
import postador 
import google.generativeai as genai
import json

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- INTELIGÊNCIA DE TENDÊNCIAS (PROMPT DE ELITE INTEGRADO) ---
def get_nexus_intelligence():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
        hoje = datetime.now().strftime("%d/%m/%Y")
        
        # O SEU PROMPT DE PESQUISA VIRAL
        prompt = f"""
        Pesquise as tendências virais de hoje ({hoje}) no TikTok Brasil, Instagram Reels e YouTube Shorts. 
        Cruze esses dados com o volume de busca no Google Trends. 
        Identifique as 5 músicas ou áudios com maior potencial de conversão e sugira um gancho AIDA para cada uma. 
        Retorne o resultado EXCLUSIVAMENTE em formato JSON puro no formato: 
        {{"trends": [
            {{"musica": "nome", "score": 95, "razao": "tendência alta", "aida_hook": "Atenção:..."}}
        ]}}
        """
        
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e)}

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS ---
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
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}_{valor[:3]}"):
            st.session_state.sel_nome = n_exibir
            st.session_state.sel_link = link
            st.session_state.sel_preco = valor
            update.registrar_mineracao(n_exibir, link, calor_num)
            st.toast(f"Alvo Selecionado: {n_exibir}")

# --- 3. SISTEMA DE ACESSO ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Acesso:", type="password")
        if st.button("AUTENTICAR", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- 4. ESTADO DA SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
# Adicionada KEY única para evitar o erro Duplicate ID
st.session_state.mkt_global = st.sidebar.selectbox(
    "Marketplace Ativo:", 
    ["Shopee", "Mercado Livre", "Amazon"], 
    key="mkt_global_selector"
)
motor_ia = "groq" 

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        # Adicionada KEY única
        qtd_produtos = st.selectbox("Volume:", [15, 30, 45], index=0, key="scanner_volume")
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho:", value="Cozinha Criativa", key="foco_nicho")

    if st.button(f"🔥 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando produtos com Groq..."):
            prompt_scanner = f"Não escreva introdução. Liste {qtd_produtos} produtos de {st.session_state.mkt_global} para '{foco_nicho}'. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
    
    if st.session_state.res_busca:
        st.divider()
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            linha_p = linha.replace("**", "").replace("*", "").strip()
            if "|" in linha_p:
                try:
                    partes = [p.strip() for p in linha_p.split('|')]
                    dados = {}
                    for p in partes:
                        if ":" in p:
                            k, v = p.split(":", 1)
                            dados[k.strip().upper()] = v.strip()
                    
                    n_f = "Produto Detectado"
                    for chave in dados.keys():
                        if "NOME" in chave:
                            n_f = dados[chave]
                            break
                    
                    if n_f == "Produto Detectado" and partes:
                        n_f = partes[0].split(":", 1)[-1].strip() if ":" in partes[0] else partes[0]
                    
                    v_f = dados.get("VALOR", "R$ ---")
                    c_raw = dados.get("CALOR", "0")
                    t_f = dados.get("TICKET", "Médio")
                    u_f = dados.get("URL", "#")

                    renderizar_card_produto(idx, n_f, v_f, c_raw, t_f, u_f, st.session_state.mkt_global)
                except: continue

# --- CONEXÃO COM AS OUTRAS ABAS ---
with tabs[1]: 
    arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)

with tabs[2]:
    st.header("📈 Monitor de Tendências Virais")
    if st.button("🔄 Sincronizar Tendências de Elite (Músicas + AIDA)", key="btn_sync_trends"):
        with st.spinner("Cruzando dados TikTok + Reels + Google..."):
            data = get_nexus_intelligence()
            if "trends" in data:
                st.session_state.dados_trends = data["trends"]
                st.success("Tendências de hoje sincronizadas!")
            else:
                st.error("Erro ao minerar JSON.")
    
    if "dados_trends" in st.session_state:
        for item in st.session_state.dados_trends:
            with st.expander(f"🎵 {item['musica']} - Score: {item['score']}%"):
                st.write(f"**Gancho AIDA:** {item['aida_hook']}")
                st.caption(f"**Razão:** {item['razao']}")
    
    trends.exibir_trends()

with tabs[3]: estudio.exibir_estudio(miny, motor_ia)
with tabs[4]: postador.exibir_postador(miny, motor_ia)
with tabs[5]: update.dashboard_performance_simples()
with tabs[6]: radar_engine.exibir_radar()
