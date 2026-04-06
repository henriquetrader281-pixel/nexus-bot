import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- 1. CONEXÃO MODULAR ---
try:
    import gemini_engine as gemini
    import producao_midia as midia
    import agendador as agenda
    import radar_engine as radar
    MODULOS_OK = True
except ImportError:
    MODULOS_OK = False

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Absolute V100", layout="wide", page_icon="🔱")

# --- 3. DATABASE ATUALIZADO ---
DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    # Criando com as novas colunas: valor e ticket
    pd.DataFrame(columns=[
        "data", "produto", "valor", "ticket", "status", "views", "cliques", "vendas", "faturamento", "copy", "link"
    ]).to_csv(DATA_PATH, index=False)

# --- 4. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Senha:", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- 5. MOTORES DE IA ---
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inicialização de estados (Adicionados sel_valor e sel_ticket)
for key in ["res_busca", "sel_nome", "sel_link", "copy_ativa", "sel_valor", "sel_ticket"]:
    if key not in st.session_state: st.session_state[key] = ""

def gerar_ia(prompt, system_msg="Seja direto e focado em conversão."):
    if st.session_state.get("motor_ia") == "Gemini" and MODULOS_OK:
        return gemini.perguntar_gemini(prompt, system_instruction=system_msg)
    else:
        res = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content": system_msg}, {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content

# --- 6. INTERFACE PRINCIPAL ---
st.sidebar.title("⚙️ Nexus Core")
st.session_state.motor_ia = st.sidebar.selectbox("Cérebro Ativo:", ["Groq", "Gemini"])

tabs = st.tabs(["🔎 Scanner", "⚔️ Arsenal 10x", "🔥 Radar", "🎥 Estúdio", "📊 Performance"])

# --- ABA 0: SCANNER (COM PREÇO E TICKET) ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências")
    nicho = st.text_input("Nicho alvo:", value="Cozinha")
    if st.button("🚀 Minerar Produtos", use_container_width=True):
        # Prompt atualizado para forçar o Ticket e Valor
        p = f"Liste 20 produtos de {nicho}. Formato exato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | TICKET: [Baixo/Médio/Alto] | URL: [link]"
        st.session_state.res_busca = gerar_ia(p, "Retorne apenas a lista separada por pipes. Não saude, não comente.")
        st.rerun()

    if st.session_state.res_busca:
        limpo = st.session_state.res_busca.replace("**", "").replace("Aqui está", "").strip()
        linhas = [l.strip() for l in limpo.split('\n') if "|" in l]
        
        for idx, linha in enumerate(linhas):
            try:
                parts = [p.strip() for p in linha.split("|")]
                nome = parts[0].split("NOME:")[1].strip() if "NOME:" in parts[0] else parts[0]
                calor = int(''.join(filter(str.isdigit, parts[1])))
                valor = parts[2].split("VALOR:")[1].strip() if "VALOR:" in parts[2] else parts[2]
                ticket = parts[3].split("TICKET:")[1].strip() if "TICKET:" in parts[3] else "Médio"
                link_orig = parts[4].split("URL:")[1].strip() if "URL:" in parts[4] else "https://shopee.com.br"
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.write(f"📦 **{nome}**")
                        st.caption(f"💰 {valor} | 🏷️ Ticket: {ticket}")
                    with c2:
                        st.progress(min(calor/100, 1.0))
                        st.write(f"🌡️ {calor}°C")
                    with c3:
                        if st.button("Selecionar", key=f"s_{idx}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link_orig
                            st.session_state.sel_valor = valor
                            st.session_state.sel_ticket = ticket
                            st.toast(f"✅ {nome} capturado!")
            except:
                continue

# --- ABA 3: ESTÚDIO (INTEGRADO COM AGENDADOR) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    st.caption(f"Valor: {st.session_state.sel_valor} | Ticket: {st.session_state.sel_ticket}")
    copy_f = st.text_area("Roteiro:", value=st.session_state.copy_ativa, height=150)
    
    if st.button("🚀 Agendar e Produzir"):
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_deep = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
        
        if MODULOS_OK:
            # Enviando todos os dados para o agendador
            status = agenda.salvar_na_fila(prod_f, copy_f, link_deep, st.session_state.sel_valor, st.session_state.sel_ticket)
            st.success(status)
            midia.gerar_video_ia(prod_f, copy_f)
        else:
            st.warning("Módulos de produção offline. Verifique os ficheiros.")

# --- ABA 4: PERFORMANCE (VISUALIZAÇÃO COMPLETA) ---
with tabs[4]:
    st.header("📊 Painel de Performance")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        st.dataframe(df, use_container_width=True)
