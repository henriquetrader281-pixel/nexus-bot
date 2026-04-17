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
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{ico} {nome}**")
            st.caption(f"🔗 {link[:50]}...")
            
        with col2:
            st.markdown(f"💰 **{valor}**")
            st.markdown(f"🏷️ Ticket: **{ticket}**")
            
        with col3:
            st.metric("🔥 Calor", f"{calor}°C")
            if st.button("🎯 Selecionar", key=f"btn_{idx}"):
                st.session_state.sel_nome = nome
                st.session_state.sel_link = link
                st.success(f"Selecionado: {nome}")
                st.rerun()

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
        st.session_state.motor_ia_obj = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        st.error(f"Falha ao carregar motor IA: {e}")

# --- 5. INTERFACE PRINCIPAL ---
st.sidebar.title("🔱 Nexus Control")
st.session_state.mkt_global = st.sidebar.selectbox("Marketplace Ativo:", ["Shopee", "Mercado Livre", "Amazon"])
debug_scanner = st.sidebar.checkbox("🔬 Debug Scanner (raw output)", value=False)

tabs = st.tabs(["🔍 SCANNER", "🚀 ARSENAL", "📈 TRENDS", "🎥 ESTÚDIO", "🛰️ POSTADOR", "📊 DASHBOARD", "🌍 RADAR"])
# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header(f"🔍 Scanner Nexus: {st.session_state.mkt_global}")
    
    qtd_produtos = st.selectbox("Quantidade de achados:", [5, 10, 15, 20], index=0)
    
    if st.button("🚀 INICIAR VARREDURA DE ELITE", use_container_width=True):
        with st.spinner("Minerando dados..."):
            prompt_scanner = f"Liste {qtd_produtos} produtos virais da {st.session_state.mkt_global}. Retorne EXATAMENTE assim para cada: NOME: [nome] | VALOR: [preço] | CALOR: [numero] | TICKET: [Baixo/Médio/Alto] | LINK: [url] ###"
            
            # Chama o minerador
            resultado_raw = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, st.session_state.motor_ia_obj)
            
            if resultado_raw:
                # Limpa e separa os produtos pelo marcador ###
                st.session_state.lista_produtos = [p.strip() for p in resultado_raw.split("###") if "NOME:" in p]
                st.success(f"✅ {len(st.session_state.lista_produtos)} Oportunidades detectadas!")

    # --- LISTAGEM COM LAYOUT CORRIGIDO ---
    if st.session_state.get("lista_produtos"):
        for idx, bloco in enumerate(st.session_state.lista_produtos):
            dados = {}
            for item in bloco.split("|"):
                if ":" in item:
                    chave, valor = item.split(":", 1)
                    dados[chave.strip()] = valor.strip()
            
            # Renderiza o card com os dados extraídos
            renderizar_card_produto(
                idx, 
                dados.get("NOME", "Produto Sem Nome"), 
                dados.get("VALOR", "Consultar"), 
                dados.get("CALOR", "50"), 
                dados.get("TICKET", "Médio"), 
                dados.get("LINK", ""), 
                st.session_state.mkt_global
            )
            except:
                continue      # Chama o minerador (Llama 3.3 via Groq)
            resultado_raw = miny.minerar_produtos(prompt_scanner, st.session_state.mkt_global, st.session_state.motor_ia_obj)
            
            if resultado_raw:
                st.session_state.lista_produtos = resultado_raw
                st.success("Varredura concluída!")
