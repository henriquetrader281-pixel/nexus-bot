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
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"Analise tendências virais de HOJE ({hoje}) no TikTok Brasil e Instagram Reels. Retorne APENAS JSON."
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

# --- 4. ESTADO DA SESSÃO E DEFINIÇÕES GLOBAIS ---
motor_ia = "groq" # Define globalmente para evitar NameError na linha 165

if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

if "motor_ia_obj" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.error("Erro ao iniciar Gemini.")

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace Ativo:", ["Shopee", "Mercado Livre", "Amazon"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER (VERSÃO RESTAURADA E BLINDADA) ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Volume de Mineração:", [15, 30, 45], index=1)
    
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho da Operação:", value="Cozinha Criativa", key="nicho_input")

    if st.button(f"🔥 INICIAR VARREDURA {st.session_state.mkt_global.upper()}", use_container_width=True):
        with st.spinner(f"Nexus minerando produtos virais em '{foco_nicho}'..."):
            prompt_scanner = f"Liste {qtd_produtos} produtos da {st.session_state.mkt_global} para '{foco_nicho}'. Formato: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            st.session_state.res_busca = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            linha_limpa = linha.replace("**", "").replace("*", "").strip()
            
            if "|" in linha_limpa:
                try:
                    partes_lista = [p.strip() for p in linha_limpa.split('|')]
                    dados = {}
                    for p in partes_lista:
                        if ':' in p:
                            k, v = p.split(':', 1)
                            # Limpa a chave de números e pontos (ex: "1. NOME" vira "NOME")
                            k_clean = "".join([c for c in k if not c.isdigit()]).replace(".", "").strip().upper()
                            dados[k_clean] = v.strip()
                    
                    # BUSCA FLEXÍVEL POR NOME
                    nome_f = "Produto Desconhecido"
                    for k in dados:
                        if "NOME" in k or "PRODUTO" in k:
                            nome_f = dados[k]
                            break
                    
                    # Fallback para o Nome se a IA inverter os campos (Evita exibir "CALOR: 85")
                    if "CALOR" in nome_f.upper() or nome_f == "Produto Desconhecido":
                        for p in partes_lista:
                            if ":" in p and "CALOR" not in p.upper():
                                nome_f = p.split(":", 1)[-1].strip()
                                break

                    # EXTRAÇÃO BLINDADA DO LINK
                    link_f = "#"
                    for k, v in dados.items():
                        if "URL" in k or "LINK" in k or "HTTP" in v.upper():
                            link_f = v.replace(" ", "")
                            break
                    
                    ticket_val = dados.get("TICKET", "Médio")
                    
                    if ticket_val in filtro_ticket:
                        c_str = "".join(filter(str.isdigit, str(dados.get("CALOR", "0"))))
                        renderizar_card_produto(idx, nome_f, dados.get("VALOR", "---"), int(c_str) if c_str else 0, ticket_val, link_f, st.session_state.mkt_global)
                except:
                    continue

# --- CONEXÃO COM AS OUTRAS ABAS ---
# --- CONEXÃO COM AS OUTRAS ABAS ---
with tabs[1]: 
    if "motor_ia_obj" in st.session_state:
        # Passa o motor Gemini configurado para o Arsenal
        arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
    else:
        st.error("Cérebro IA offline. Dê reboot no sistema.")

with tabs[2]: 
    trends.exibir_trends()

with tabs[3]: 
    estudio.exibir_estudio(miny, motor_ia)

with tabs[4]: 
    postador.exibir_postador(miny, motor_ia)

with tabs[5]: 
    update.dashboard_performance_simples()

with tabs[6]: 
    radar_engine.exibir_radar()
