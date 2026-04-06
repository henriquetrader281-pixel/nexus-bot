import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- 1. CONFIGURAÇÃO E LOGIN (SECRETS) ---
st.set_page_config(page_title="Nexus Absolute V85", layout="wide", page_icon="🔱")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Busca a senha diretamente do Secrets para segurança total
        senha_mestra = st.secrets.get("NEXUS_PASSWORD", "Bru2024!")
        senha = st.text_input("Insira a senha de acesso:", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if senha == senha_mestra:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- 2. CONEXÃO COM MOTORES (GROQ & GEMINI) ---
try:
    # Motor Groq (Llama 3.3) - Busca Key no Secrets
    client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Preparação para o Motor Gemini (Arquivo .py que vamos adicionar)
    gemini_key = st.secrets.get("GEMINI_API_KEY", "AGUARDANDO_KEY")
except Exception as e:
    st.error(f"Erro de Configuração: Verifique o campo GROQ_API_KEY no seu Secrets.")

# --- 3. MEMÓRIA DE SESSÃO ---
if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""

# --- 4. FUNÇÕES DE INTELIGÊNCIA ---
def gerar_ia_groq(prompt):
    try:
        res = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content":"Você é um minerador de dados. Responda APENAS no formato solicitado, sem textos extras."},
                      {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    except: return "ERRO_GROQ"

def gerar_ia_gemini(prompt):
    # Espaço reservado para a lógica de programação que faremos no Gemini.py
    return "Módulo Gemini em fase de integração de programação..."

# --- 5. INTERFACE PRINCIPAL ---
st.title("🔱 Nexus Absolute: Full Intelligence")

tabs = st.tabs([
    "🔎 Scanner 30x", 
    "⚔️ Arsenal 10x", 
    "🔥 Radar & Termômetro", 
    "🎥 Estúdio IA", 
    "📊 Dashboard Master"
])

# --- ABA 0: SCANNER (RESTAURADO COM ÍCONES E VALORES) ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências High-Ticket")
    c1, c2, c3 = st.columns([2, 1, 1])
    nicho = c1.text_input("Nicho alvo:", value="Utilidades Domésticas")
    ticket_sel = c2.selectbox("Ticket Médio:", ["Baixo (R$20-80)", "Médio (R$80-250)", "Alto (R$250+)"])
    
    if st.button("🚀 Iniciar Mineração Massiva", use_container_width=True):
        with st.status("Minerando e Calculando Crescimento..."):
            # Prompt reforçado para não quebrar a busca
            p = f"""Liste 30 produtos de {nicho} na Shopee Brasil com ticket {ticket_sel}. 
            Responda EXATAMENTE neste formato para cada item:
            NOME: [nome] | CALOR: [numero 0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"""
            st.session_state.res_busca = gerar_ia_groq(p)
            st.rerun()

    if st.session_state.res_busca:
        for idx, linha in enumerate(st.session_state.res_busca.split('\n')):
            if "|" in linha and "NOME:" in linha:
                try:
                    parts = linha.split("|")
                    nome = parts[0].split("NOME:")[1].strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    valor = parts[2].split("VALOR:")[1].strip()
                    cresc = parts[3].split("CRESC:")[1].strip()
                    link_orig = parts[4].split("URL:")[1].strip()
                    
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"📦 **{nome}**")
                            st.caption(f"💰 Valor Est.: {valor} | 📈 Crescimento: {cresc}")
                        with col2:
                            st.write(f"🌡️ {calor}°C")
                            st.progress(min(calor/100, 1.0))
                        with col3:
                            st.write("🚀 **Status**")
                            st.markdown("🔥 `ESCALANDO`" if calor > 70 else "✅ `ESTÁVEL`")
                        with col4:
                            if st.button("Selecionar", key=f"sel_{idx}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link_orig
                                st.toast(f"✅ {nome} carregado no Arsenal!")
                except: continue

# --- ABA 1: ARSENAL (GERADOR DE 10 VARIAÇÕES) ---
with tabs[1]:
    st.header("⚔️ Arsenal de Escala 10x")
    if st.session_state.sel_nome:
        st.success(f"🎯 Alvo Ativo: {st.session_state.sel_nome}")
        if st.button("🔥 DISPARAR 10 VARIAÇÕES VIRAIS"):
            with st.spinner("Gerando Munição..."):
                p_ars = f"Crie 10 roteiros curtos (15s) para TikTok do produto {st.session_state.sel_nome}. Varie entre Curiosidade, Dor, Medo e Prova Social. Separe com ###"
                variacoes = [v.strip() for v in gerar_ia_groq(p_ars).split("###") if len(v) > 10]
                for i, v in enumerate(variacoes):
                    with st.container(border=True):
                        st.subheader(f"Variação V{i+1}")
                        st.write(v)
                        if st.button(f"Usar V{i+1} no Estúdio", key=f"u_{i}"):
                            st.session_state.copy_ativa = v
                            st.toast("Roteiro enviado!")
    else: st.warning("Selecione um produto no Scanner.")

# --- ABA 3: ESTÚDIO (CONECTADO AO SECRETS) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia IA")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    copy_f = st.text_area("Roteiro Selecionado:", value=st.session_state.get("copy_ativa", ""), height=150)
    
    if st.button("🚀 Produzir Mídia Completa"):
        webhook = st.secrets.get("WEBHOOK_POST_URL")
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        if webhook:
            link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"
            requests.post(webhook, json={"prod": prod_f, "copy": copy_f, "link": link_final})
            st.success("✅ Comando enviado para Lyria 3 e Nano Banana!")
