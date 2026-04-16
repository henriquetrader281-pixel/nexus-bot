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
# --- Dentro do Estado da Sessão no app.py ---
# No app.py, altera para esta configuração:
# --- Procure este trecho no seu app.py ---
if "motor_ia_obj" not in st.session_state:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # ALTERAÇÃO AQUI: Adicione o sufixo '-latest'
    st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace Ativo:", ["Shopee", "Mercado Livre", "Amazon"])
motor_ia = "groq" 

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

# --- ABA 0: SCANNER (Versão Restaurada de Alta Precisão) ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        qtd_produtos = st.selectbox("Volume de Mineração:", [15, 30, 45], index=1)
    
    with col_sel2:
        # Recupera o valor do nicho do estado da sessão se existir
        nicho_padrao = st.session_state.get('foco_nicho', "Cozinha Criativa")
        foco_nicho = st.text_input("🎯 Nicho da Operação:", value=nicho_padrao, key="nicho_input")
        st.session_state.foco_nicho = foco_nicho

    if st.button(f"🔥 INICIAR VARREDURA {st.session_state.mkt_global.upper()}", use_container_width=True):
        with st.spinner(f"Nexus minerando produtos virais em '{foco_nicho}'..."):
            prompt_scanner = f"""
            Liste {qtd_produtos} produtos físicos da {st.session_state.mkt_global} para o nicho '{foco_nicho}'.
            Formato por linha: NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link]
            """
            resultado = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)
            st.session_state.res_busca = resultado
    
    if st.session_state.res_busca:
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        for idx, linha in enumerate(linhas):
            # A DIFERENÇA: Limpeza agressiva de asteriscos para evitar erros de split
            linha_limpa = linha.replace("**", "").replace("*", "").strip()
            
            if "|" in linha_limpa:
                try:
                    partes_lista = [p.strip() for p in linha_limpa.split('|')]
                    dados = {}
                    for p in partes_lista:
                        if ':' in p:
                            k, v = p.split(':', 1)
                            dados[k.strip().upper()] = v.strip()
                    
                    # A DIFERENÇA: Busca flexível por qualquer chave que contenha "NOME"
                    nome_final = "Produto Desconhecido"
                    for chave in dados.keys():
                        if "NOME" in chave:
                            nome_final = dados[chave]
                            break
                    
                    # FALLBACK: Se a IA não enviou a chave, pega a 1ª coluna e limpa o rótulo
                    if nome_final == "Produto Desconhecido" and partes_lista:
                        nome_final = partes_lista[0].replace("NOME:", "").strip()

                    # EXTRAÇÃO DE TICKET
                    ticket_val = "Médio"
                    for chave in dados.keys():
                        if "TICKET" in chave: 
                            ticket_val = dados[chave]
                            break
                    
                    # FILTRO E RENDERIZAÇÃO
                    if ticket_val in filtro_ticket:
                        # A DIFERENÇA: Filtro de dígitos puro para o CALOR
                        c_str = "".join(filter(str.isdigit, str(dados.get("CALOR", "0"))))
                        
                        renderizar_card_produto(
                            idx, 
                            nome_final, 
                            dados.get("VALOR", "R$ ---"), 
                            int(c_str) if c_str else 0, 
                            ticket_val, 
                            dados.get("URL", "#"), 
                            st.session_state.mkt_global
                        )
                except:
                    continue

# --- CONEXÃO COM AS OUTRAS ABAS ---
with tabs[1]: 
    # Chama o Arsenal passando o motor Gemini para copys persuasivas
    arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)

with tabs[2]:
    trends.exibir_trends()
    if st.button("📊 EXECUTAR ANÁLISE GLOBAL", key="btn_trends_global"):
        intel = get_nexus_intelligence()
        if "trends" in intel:
            for item in intel["trends"]: st.write(f"🎵 {item['musica']} ({item['score']}%)")

with tabs[3]: estudio.exibir_estudio(miny, motor_ia)
with tabs[4]: postador.exibir_postador(miny, motor_ia)
with tabs[5]: update.dashboard_performance_simples()
with tabs[6]: radar_engine.exibir_radar()
