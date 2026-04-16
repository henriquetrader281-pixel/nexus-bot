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

# --- INTELIGÊNCIA DE TENDÊNCIAS ---
def get_nexus_intelligence():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search": {}}]
        )
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"Analise tendências virais de HOJE ({hoje}) no TikTok Brasil e Instagram Reels. Retorne APENAS JSON: {{\"trends\": [{{\"musica\": \"nome\", \"score\": 95, \"razao\": \"...\", \"aida_hook\": \"...\"}}]}}"
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e)}

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE CARDS (LÓGICA BLINDADA) ---
def renderizar_card_produto(idx, nome, valor, calor, ticket, link, mkt_alvo):
    icones = {"Shopee": "🧡", "Mercado Livre": "💛", "Amazon": "💙"}
    ico = icones.get(mkt_alvo, "🛍️")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            # Garante que o nome não venha vazio
            n_exibir = nome.replace("*", "").strip() if nome else "Produto Detectado"
            st.markdown(f"**{ico} {n_exibir}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        with c2:
            try:
                # Limpeza de calor: extrai apenas números para a barra azul funcionar
                c_string = "".join(filter(str.isdigit, str(calor)))
                calor_num = min(max(int(c_string), 0), 100) if c_string else 0
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", use_container_width=True):
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
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace Ativo:", ["Shopee", "Mercado Livre", "Amazon"])
motor_ia = "groq" 

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

if st.session_state.res_busca:
        st.divider()
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            # Limpeza radical: remove negritos e espaços extras antes de processar
            linha_processada = linha.replace("**", "").strip()
            
            if "|" in linha_processada:
                try:
                    partes = [p.strip() for p in linha_processada.split('|')]
                    dados = {}
                    
                    for p in partes:
                        if ":" in p:
                            # Divide no primeiro ":" e limpa chaves/valores
                            k_v = p.split(":", 1)
                            chave = k_v[0].strip().upper()
                            valor = k_v[1].strip()
                            dados[chave] = valor
                    
                    # --- CAPTURA DE NOME (MÉTODO À PROVA DE FALHAS) ---
                    # 1. Tenta achar pela chave NOME
                    n_f = dados.get("NOME")
                    
                    # 2. Se não achar, pega o que estiver antes do primeiro ":" da linha
                    if not n_f:
                        primeira_coluna = partes[0]
                        n_f = primeira_coluna.split(":", 1)[-1].strip() if ":" in primeira_coluna else primeira_coluna
                    
                    # --- CAPTURA DE DEMAIS DADOS ---
                    v_f = dados.get("VALOR", "R$ ---")
                    t_f = dados.get("TICKET", "Médio")
                    u_f = dados.get("URL", "#")

                    # --- TRATAMENTO DE CALOR (Para a barra azul) ---
                    c_raw = dados.get("CALOR", "0")
                    # Extrai apenas os números (remove % , °C, etc)
                    c_num = "".join(filter(str.isdigit, str(c_raw)))
                    c_f = int(c_num) if c_num else 0
                    
                    # Fallback Calor: Se veio zerado, tenta pegar qualquer número da 2ª parte
                    if c_f == 0 and len(partes) > 1:
                        fallback_c = "".join(filter(str.isdigit, partes[1]))
                        c_f = int(fallback_c) if fallback_c else 0

                    # Renderiza o Card com o nome forçado
                    renderizar_card_produto(idx, n_f, v_f, c_f, t_f, u_f, st.session_state.mkt_global)
                    
                except Exception as e:
                    continue
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
                    
                    # LÓGICA DE CAPTURA DE NOME ROBUSTA (Resolve o erro do nome sumir)
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

# --- CONEXÃO COM AS OUTRAS ABAS ---
with tabs[1]: 
    # Passa o Gemini (motor_ia_obj) para o Arsenal para gerar copys com AIDA e CTA
    arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)

with tabs[2]:
    trends.exibir_trends()
    if st.button("📊 EXECUTAR ANÁLISE GLOBAL"):
        intel = get_nexus_intelligence()
        if "trends" in intel:
            for item in intel["trends"]: st.write(f"🎵 {item['musica']} ({item['score']}%)")

with tabs[3]: estudio.exibir_estudio(miny, motor_ia)
with tabs[4]: postador.exibir_postador(miny, motor_ia)
with tabs[5]: update.dashboard_performance_simples()
with tabs[6]: radar_engine.exibir_radar()
