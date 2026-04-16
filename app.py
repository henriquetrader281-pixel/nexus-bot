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

# --- INTELIGÊNCIA DE TENDÊNCIAS (NÍVEL ELITE) ---
def get_nexus_intelligence():
    """Busca as 5 tendências elite cruzando TikTok e Instagram via Gemini"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search": {}}]
        )
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"""
        Aja como um especialista em tendências virais de e-commerce. 
        Analise tendências de HOJE ({hoje}) no TikTok Brasil e Instagram Reels para o nicho de Achadinhos/Shopee.
        Identifique as 5 músicas ou estilos de áudio em curva ascendente.
        Retorne APENAS um JSON puro no formato: 
        {{"trends": [{{"musica": "nome", "score": 95, "razao": "explicação", "aida_hook": "gancho viral"}}]}}
        """
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {
            "trends": [
                {"musica": "Brazilian Funk Instrumental", "score": 98, "razao": "Alta conversão", "aida_hook": "SÓ 17 REAIS? 😱"},
                {"musica": "Aesthetic Lofi Beats", "score": 92, "razao": "Viral para nicho de organização", "aida_hook": "VOCÊ PRECISA DISSO! ✨"}
            ]
        }

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (LIMPEZA ELITE) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            # Garante que o nome não venha vazio
            exibir_nome = nome if nome else "Produto Detectado"
            st.markdown(f"**{ico} {exibir_nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        with c2:
            try:
                # Limpeza de Calor: remove qualquer texto e deixa só números
                c_string = "".join(filter(str.isdigit, str(calor)))
                calor_num = min(max(int(c_string), 0), 100) if c_string else 0
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", use_container_width=True):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.session_state.sel_preco = valor
            update.registrar_mineracao(nome, link, calor_num)
            st.toast(f"Alvo Selecionado: {nome}")

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
if "sel_preco" not in st.session_state: st.session_state.sel_preco = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace Ativo:", ["Shopee", "Mercado Livre", "Amazon"])
motor_ia_nome = st.sidebar.selectbox("Cérebro de IA:", ["gemini-1.5-flash", "gemini-1.5-pro"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER (LÓGICA BLINDADA) ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Volume:", [15, 30, 45], index=1)
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho:", value="Cozinha Criativa", key="foco_nicho")

    if st.button(f"🔥 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando produtos com Groq..."):
            prompt_scanner = f"Não escreva introdução. Liste {qtd_produtos} produtos de {st.session_state.mkt_global} para '{foco_nicho}'. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia_nome)
    
    if st.session_state.res_busca:
        st.divider()
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            linha_limpa = linha.strip()
            if "|" in linha_limpa:
                try:
                    partes = [p.strip() for p in linha_limpa.split('|')]
                    dados = {}
                    for p in partes:
                        p_analise = p.replace("*", "").strip()
                        if ":" in p_analise:
                            k, v = p_analise.split(":", 1)
                            dados[k.strip().upper()] = v.strip()
                    
                    # CAPTURA DE NOME COM FALLBACK (Não falha se sumir "NOME:")
                    n_f = dados.get("NOME")
                    if not n_f:
                        primeira_parte = partes[0].replace("*", "").strip()
                        n_f = primeira_parte.split(":")[-1].strip() if ":" in primeira_parte else primeira_parte
                    
                    v_f = dados.get("VALOR", "R$ ---")
                    c_f = dados.get("CALOR", "0")
                    t_f = dados.get("TICKET", "Médio")
                    u_f = dados.get("URL", "#")

                    renderizar_card_produto(idx, n_f, v_f, c_f, t_f, u_f, st.session_state.mkt_global)
                except: continue

# --- CONEXÃO DAS DEMAIS ABAS ---
with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]:
    trends.exibir_trends()
    if st.button("📊 EXECUTAR ANÁLISE MONITOR GLOBAL", use_container_width=True):
        with st.spinner("Sincronizando Tendências Elite..."):
            intel = get_nexus_intelligence()
            if "trends" in intel:
                st.session_state.cache_trends = intel["trends"]
                st.rerun()

with tabs[3]: estudio.exibir_estudio(miny, st.session_state.motor_ia_obj)
with tabs[4]: postador.exibir_postador(miny, st.session_state.motor_ia_obj)
with tabs[5]: update.dashboard_performance_simples()
with tabs[6]: radar_engine.exibir_radar()
