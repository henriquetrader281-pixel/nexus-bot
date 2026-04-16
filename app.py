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
            c_str = "".join(filter(str.isdigit, str(calor)))
            calor_num = min(max(int(c_str), 0), 100) if c_str else 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", use_container_width=True):
            st.session_state.sel_nome = n_exibir
            st.session_state.sel_link = link
            st.session_state.sel_preco = valor
            update.registrar_mineracao(n_exibir, link, calor_num)
            st.toast(f"Selecionado: {n_exibir}")

# --- 3. ACESSO E ESTADO ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Acesso:", type="password")
        if st.button("AUTENTICAR", use_container_width=True):
            if senha == st.secrets.get("NEXUS_PASSWORD", "Bru2024!"):
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Incorreto.")
    st.stop()
if not st.session_state.autenticado: login()

# Variáveis Globais para evitar NameError
motor_ia = "groq"
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

if "motor_ia_obj" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash')
    except: st.error("Erro IA")

# --- 5. INTERFACE ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace:", ["Shopee", "Mercado Livre", "Amazon"])

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER (Versão Blindada Restaurada) ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Quantidade de itens:", [15, 30, 45], index=1)
    
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho da Operação:", value="Cozinha Criativa", key="nicho_ativo")

    if st.button(f"🔥 Iniciar Varredura na {st.session_state.mkt_global}", use_container_width=True):
        with st.spinner(f"Nexus minerando produtos virais em '{foco_nicho}'..."):
            # Prompt reforçado para garantir o separador "|"
            prompt_scanner = f"Liste {qtd_produtos} produtos da {st.session_state.mkt_global} para '{foco_nicho}'. Use este formato exato por linha: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
            resultado = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
            st.session_state.res_busca = resultado
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            # LIMPEZA: Remove asteriscos que confundem o código
            linha_limpa = linha.replace("**", "").replace("*", "").strip()
            
            if "|" in linha_limpa:
                try:
                    # LÓGICA DO APP (22): Transforma a linha em um dicionário de dados
                    partes = {}
                    for p in linha_limpa.split('|'):
                        if ':' in p:
                            chave, valor = p.split(':', 1)
                            partes[chave.strip().upper()] = valor.strip()
                    
                    # CAPTURA BLINDADA DOS DADOS
                    nome_f = partes.get("NOME", "Produto Desconhecido")
                    valor_f = partes.get("VALOR", "Consultar")
                    ticket_f = partes.get("TICKET", "Médio")
                    link_f = partes.get("URL", "#")
                    
                    # Se o nome vier com "CALOR:", nós corrigimos pegando a primeira parte do split
                    if "CALOR" in nome_f.upper():
                        nome_f = linha_limpa.split('|')[0].replace("NOME:", "").strip()

                    # FILTRAGEM POR TICKET
                    if ticket_f in filtro_ticket:
                        # Extração de Calor (Garante que a barra azul não fique em 0)
                        c_raw = partes.get("CALOR", "0")
                        c_str = "".join(filter(str.isdigit, str(c_raw)))
                        calor_num = int(c_str) if c_str else 0
                        
                        renderizar_card_produto(
                            idx, 
                            nome_f, 
                            valor_f, 
                            calor_num,
                            ticket_f,
                            link_f,
                            st.session_state.mkt_global
                        )
                except Exception as e:
                    continue
# --- OUTRAS ABAS ---
with tabs[1]: arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
with tabs[3]: estudio.exibir_estudio(miny, motor_ia)
with tabs[4]: postador.exibir_postador(miny, motor_ia)
with tabs[5]: update.dashboard_performance_simples()
with tabs[6]: radar_engine.exibir_radar()
