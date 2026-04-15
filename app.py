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
import estudio  # <--- CORRIGIDO
import postador # <--- NOVO: POSTADOR AUTOMÁTICO
import google.generativeai as genai
import json

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="Nexus Absolute V101", layout="wide", page_icon="🔱")

# --- NOVO: LÓGICA DE INTELIGÊNCIA DE TENDÊNCIAS ---
def get_nexus_intelligence():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash', # Versão estável
            tools=[{"google_search": {}}]
        )
        
        hoje = datetime.now().strftime("%d/%m/%Y")
        prompt = f"""
        Analise tendências virais de HOJE ({hoje}) no TikTok Brasil e Instagram Reels.
        Retorne APENAS um JSON puro no formato:
        {{"trends": [
            {{"musica": "nome", "score": 95, "razao": "...", "aida_hook": "..."}}
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
            st.markdown(f"**{ico} {nome}**")
            st.caption(f"💰 {valor} | 🎫 {ticket}")
        
        with c2:
            try:
                calor_num = min(max(int(calor), 0), 100)
            except:
                calor_num = 0
            st.progress(calor_num / 100)
            st.write(f"🌡️ {calor_num}°C")
        
        if c3.button("🎯 Selecionar", key=f"sel_{idx}_{mkt_alvo}", width='stretch'):
            st.session_state.sel_nome = nome
            st.session_state.sel_link = link
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

if not st.session_state.autenticado:
    login()

# --- 4. ESTADO DA SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""
if "mkt_global" not in st.session_state: st.session_state.mkt_global = "Shopee"

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox(
    "Marketplace Ativo:", 
    ["Shopee", "Mercado Livre", "Amazon"], 
    index=["Shopee", "Mercado Livre", "Amazon"].index(st.session_state.mkt_global)
)

motor_ia = st.sidebar.selectbox("Cérebro de IA:", ["gpt-4o-mini", "gemini-1.5-pro"])

# 🔄 Adicionado a Aba POSTADOR no menu
tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])

if st.session_state.res_busca:
        st.divider()
        linhas = st.session_state.res_busca.split('\n')
        
        for idx, linha in enumerate(linhas):
            # Limpa a linha de negritos e espaços extras
            linha_limpa = linha.replace("**", "").replace("*", "").strip()
            
            if "|" in linha_limpa:
                try:
                    # Criamos um dicionário para mapear os dados independente da ordem
                    dados = {}
                    partes = [p.strip() for p in linha_limpa.split('|')]
                    
                    for p in partes:
                        if ":" in p:
                            chave, valor = p.split(":", 1)
                            dados[chave.strip().upper()] = valor.strip()
                    
                    # --- EXTRAÇÃO INTELIGENTE DO NOME ---
                    # Tenta pegar pela chave 'NOME', se não achar, pega a primeira parte antes do primeiro '|'
                    nome_final = dados.get("NOME")
                    if not nome_final:
                        nome_final = partes[0].replace("NOME", "").replace(":", "").strip()
                    
                    # Extração dos outros dados com valores padrão (Fallbacks)
                    calor_final = dados.get("CALOR", "0").split('°')[0].strip()
                    preco_final = dados.get("VALOR", dados.get("PREÇO", "R$ ---"))
                    ticket_final = dados.get("TICKET", "Médio")
                    url_final = dados.get("URL", dados.get("LINK", "#"))

                    # Renderiza o Card com os dados limpos
                    renderizar_card_produto(
                        idx, 
                        nome_final, 
                        preco_final, 
                        calor_final, 
                        ticket_final, 
                        url_final, 
                        st.session_state.mkt_global
                    )
                except Exception as e:
                    # Se uma linha der erro, ele pula para a próxima sem travar o Nexus
                    continue
                
                # Captura os dados reais
                nome_f = dados.get("NOME", "Produto")
                calor_f = dados.get("CALOR", "0").replace("°C", "").replace("%", "")
                preco_f = dados.get("VALOR", "R$ ---") # <--- AQUI PEGA O PREÇO
                ticket_f = dados.get("TICKET", "Médio")
                url_f = dados.get("URL", "#")
                
                renderizar_card_produto(idx, nome_f, preco_f, calor_f, ticket_f, url_f, st.session_state.mkt_global)
            except: continue

# --- ABA 1: ARSENAL ---
with tabs[1]:  
    arsenal.exibir_arsenal(miny, motor_ia)

# --- ABA 2: TRENDS ---
with tabs[2]:
    trends.exibir_trends()
    st.divider()
    if st.button("📊 EXECUTAR ANÁLISE MONITOR GLOBAL"):
        intel_data = get_nexus_intelligence()
        if "trends" in intel_data:
            for item in intel_data["trends"]:
                st.write(f"🎵 **{item['musica']}** - Confiança: {item['score']}%")
                st.caption(item['razao'])

# --- ABA 3: ESTÚDIO ---
with tabs[3]:
    estudio.exibir_estudio(miny, motor_ia) # <--- CORRIGIDO

# --- ABA 4: POSTADOR ---
with tabs[4]:
    postador.exibir_postador(miny, motor_ia) # <--- INTEGRADO

# --- ABA 5: DASHBOARD ---
with tabs[5]:
    update.dashboard_performance_simples()

# --- ABA 6: RADAR ---
with tabs[6]:
    radar_engine.exibir_radar()
