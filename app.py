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
        model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"Analise tendências virais de HOJE ({hoje}) no TikTok Brasil e Instagram Reels. Retorne APENAS JSON: {{\"trends\": [{{\"musica\": \"nome\", \"score\": 95, \"razao\": \"...\", \"aida_hook\": \"...\"}}]}}"
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
            st.markdown(f"**{ico} {nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        with c2:
            try:
                c_string = "".join(filter(str.isdigit, str(calor)))
                calor_num = min(max(int(c_string), 0), 100) if c_string else 0
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        
        # O botão agora salva os dados puros, sem tentar limpar de novo
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", use_container_width=True):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
            st.session_state.sel_preco = valor
            try:
                update.registrar_mineracao(nome, link, calor_num)
            except:
                pass # Evita travar se o banco de dados falhar
            st.toast(f"Alvo Selecionado: {nome}")

# --- 3. SISTEMA DE ACESSO ---
if "autenticado" not in st.session_state: 
    st.session_state.autenticado = False

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
            else: 
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- 4. ESTADO DA SESSÃO ---
for key in ["res_busca", "sel_nome", "sel_link"]:
    if key not in st.session_state: st.session_state[key] = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

if "motor_ia_obj" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        st.error("Erro ao iniciar o Gemini. Verifique a GEMINI_API_KEY nos Secrets.")

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace Ativo:", ["Shopee", "Mercado Livre", "Amazon"])
motor_ia = "groq" 

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER (Motor de Extração Blindado) ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Volume:", [15, 30, 45], index=0)
    with col_sel2:
        foco_nicho = st.text_input("🎯 Nicho:", value="Cozinha Criativa", key="foco_nicho")

    if st.button(f"🔥 INICIAR VARREDURA", use_container_width=True):
        with st.spinner("Minerando produtos virais..."):
            prompt_scanner = f"Não escreva introdução. Liste {qtd_produtos} produtos de {st.session_state.mkt_global} para '{foco_nicho}'. Formato OBRIGATÓRIO: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [https://...]"
            st.session_state.res_busca = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            # Limpeza inicial severa
            linha_p = linha.replace("**", "").replace("*", "").strip()
            
            # Só processa se tiver um link válido e o separador
            if "|" in linha_p and ("URL:" in linha_p.upper() or "HTTP" in linha_p.upper()):
                try:
                    partes = [p.strip() for p in linha_p.split('|')]
                    dados = {}
                    
                    # Constrói o dicionário de forma segura
                    for p in partes:
                        if ":" in p:
                            k, v = p.split(":", 1)
                            # Remove números de listas (ex: "1. NOME" vira "NOME")
                            k_clean = ''.join([i for i in k if not i.isdigit()]).replace(".", "").strip().upper()
                            dados[k_clean] = v.strip()
                    
                    # Extração garantida
                    nome_final = dados.get("NOME", "Produto Detectado")
                    link_final = dados.get("URL", "#").replace(" ", "")
                    valor_final = dados.get("VALOR", "---")
                    ticket_val = dados.get("TICKET", "Médio")
                    c_str = "".join(filter(str.isdigit, str(dados.get("CALOR", "0"))))
                    
                    if ticket_val in filtro_ticket and link_final != "#":
                        renderizar_card_produto(
                            idx, nome_final, valor_final, int(c_str) if c_str else 0, 
                            ticket_val, link_final, st.session_state.mkt_global
                        )
                except Exception as e:
                    continue # Se a linha falhar totalmente, pula para a próxima sem travar

# --- CONEXÃO COM AS OUTRAS ABAS ---
with tabs[1]: 
    if "motor_ia_obj" in st.session_state:
        arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
    else:
        st.error("Cérebro IA offline. Dê reboot no sistema.")

with tabs[2]: trends.exibir_trends()
with tabs[3]: estudio.exibir_estudio(miny, motor_ia)
with tabs[4]: postador.exibir_postador(miny, motor_ia)
with tabs[5]: update.dashboard_performance_simples()
with tabs[6]: radar_engine.exibir_radar()
