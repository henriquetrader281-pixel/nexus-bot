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
        model = genai.GenerativeModel(model_name='gemini-1.5-pro')
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

# --- 4. ESTADO DA SESSÃO E MOTOR IA ---
motor_ia = "groq" 

if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

if "motor_ia_obj" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 🔱 Como você tem Gemini Plus, usamos o 1.5-PRO para mineração de elite
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        st.error(f"Falha ao carregar motor IA: {e}")

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace Ativo:", ["Shopee", "Mercado Livre", "Amazon"])
debug_scanner = st.sidebar.checkbox("🔬 Debug Scanner (raw output)", value=False)

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

for idx, linha in enumerate(linhas):
            # 1. Limpeza total de lixo visual
            l_limpa = linha.replace("**", "").replace("*", "").strip()
            
            if "|" in l_limpa:
                try:
                    # 2. Divide a linha em partes e mapeia num dicionário
                    partes_brutas = [p.strip() for p in l_limpa.split('|')]
                    dados = {}
                    for p in partes_brutas:
                        if ":" in p:
                            k, v = p.split(":", 1)
                            # Remove números de lista (ex: '1. NOME' vira 'NOME')
                            k_clean = "".join([i for i in k if not i.isdigit()]).replace(".", "").strip().upper()
                            dados[k_clean] = v.strip()
                    
                    # 🔱 3. RESGATE DO NOME (NÃO ACEITA 'CALOR' NO NOME)
                    nome_f = ""
                    # Busca direta pela chave
                    for chave in dados.keys():
                        if "NOME" in chave or "PRODUTO" in chave:
                            nome_f = dados[chave]
                            break
                    
                    # Validação: Se o nome capturado contém 'CALOR' ou está vazio, busca em outras partes
                    if not nome_f or "CALOR" in nome_f.upper():
                        for pb in partes_brutas:
                            if ":" in pb:
                                cabecalho, conteudo = pb.split(":", 1)
                                if "CALOR" not in cabecalho.upper() and "URL" not in cabecalho.upper():
                                    nome_f = conteudo.strip()
                                    break

                    # 4. EXTRAÇÃO DO CALOR (MATA O ERRO DE 0°C)
                    # Pega apenas os números, ignorando o texto 'CALOR:'
                    calor_raw = dados.get("CALOR", "0")
                    c_str = "".join(filter(str.isdigit, str(calor_raw)))
                    calor_num = int(c_str) if c_str else 0

                    # 5. DEMAIS DADOS E LINK
                    valor_f = dados.get("VALOR", "---")
                    ticket_f = dados.get("TICKET", "Médio")
                    
                    link_raw = dados.get("URL", dados.get("LINK", "#"))
                    link_f = str(link_raw).replace(" ", "").replace("(", "").replace(")", "").strip()

                    # 6. RENDERIZAÇÃO
                    if ticket_f in filtro_ticket:
                        renderizar_card_produto(
                            idx, 
                            nome_f, 
                            valor_f, 
                            calor_num, 
                            ticket_f, 
                            link_f, 
                            st.session_state.mkt_global
                        )
                except:
                    continue
Use estes critérios de TICKET:
- BAIXO: Até R$ 50
- MÉDIO: R$ 51 até R$ 200
- ALTO: Acima de R$ 200
NÃO use markdown ou formatação nos links.
FORMATO OBRIGATÓRIO POR LINHA:
NOME: [nome] | CALOR: [75-99] | VALOR: R$ [valor] | TICKET: [Baixo/Médio/Alto] | URL: [link_direto_sem_formatacao]"""

            st.session_state.res_busca = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, motor_ia)

    if st.session_state.res_busca:
        if debug_scanner:
            st.text_area("🔬 Raw output da IA:", st.session_state.res_busca, height=300)
        
        st.divider()
        filtro_ticket = st.multiselect("Filtrar por Ticket:", ["Baixo", "Médio", "Alto"], default=["Baixo", "Médio", "Alto"])
        
        linhas = st.session_state.res_busca.split('\n')
        produtos_renderizados = 0

        for idx, linha in enumerate(linhas):
            l_p = linha.replace("**", "").replace("*", "").strip()
            
            if "|" in l_p:
                try:
                    partes = [p.strip() for p in l_p.split('|')]
                    dados = {}
                    for p in partes:
                        if ":" in p:
                            k, v = p.split(":", 1)
                            k_c = "".join([i for i in k if not i.isdigit()]).replace(".", "").strip().upper()
                            dados[k_c] = v.strip()
                    
                    # 🔱 BUSCA DE NOME BLINDADA
                    nome_f = ""
                    for c in dados.keys():
                        if "NOME" in c: nome_f = dados[c]; break
                    
                    if not nome_f or "CALOR" in nome_f.upper():
                        # Fallback se a IA inverter os campos
                        for p in partes:
                            if ":" in p and "CALOR" not in p.upper() and "URL" not in p.upper():
                                nome_f = p.split(":", 1)[-1].strip()
                                break

                    # 🔱 CAPTURA DE LINK LIMPA (Resolve o erro 404)
                    link_raw = dados.get("URL", "#")
                    link_f = str(link_raw).replace("*", "").replace(" ", "").replace("(", "").replace(")", "").strip()
                    if "http" not in link_f: link_f = "#"

                    t_v = dados.get("TICKET", "Médio")
                    if t_v in filtro_ticket:
                        c_str = "".join(filter(str.isdigit, str(dados.get("CALOR", "0"))))
                        renderizar_card_produto(idx, nome_f, dados.get("VALOR", "---"), int(c_str) if c_str else 0, t_v, link_f, st.session_state.mkt_global)
                        produtos_renderizados += 1
                except: continue

# --- CONEXÃO COM AS OUTRAS ABAS ---
with tabs[1]: 
    arsenal.exibir_arsenal(miny, st.session_state.motor_ia_obj)
with tabs[2]: trends.exibir_trends()
with tabs[3]: estudio.exibir_estudio(miny, motor_ia)
with tabs[4]: postador.exibir_postador(miny, motor_ia)
with tabs[5]: update.dashboard_performance_simples()
with tabs[6]: radar_engine.exibir_radar()
