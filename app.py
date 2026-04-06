import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Omega V27", layout="wide", page_icon="🔱")

# --- SISTEMA DE LOGIN (Mantido) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Omega Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Insira a senha de acesso:", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if senha == "Bru2024!":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

if not st.session_state.autenticado: login()

# --- INICIALIZAÇÃO DE DADOS & IA ---
DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data", "produto", "status", "vendas", "faturamento", "score"]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

if "res_busca" not in st.session_state: st.session_state.res_busca = ""
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""

def gerar_ia(prompt):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"system", "content":"Seja direto. Formate exatamente como pedido."},
                  {"role":"user","content": prompt}]
    )
    return res.choices[0].message.content

# --- INTERFACE PRINCIPAL ---
st.title("🔱 Nexus Absolute: Command Center")

tabs = st.tabs(["🔎 Scanner 30x", "⚔️ Arsenal 10x", "🔥 Radar Global", "🎥 Estúdio IA", "💰 Financeiro"])

# --- ABA 0: SCANNER (COM ÍCONES E VALORES) ---
with tabs[0]:
    st.header("🔎 Monitor de Tendências High-Ticket")
    c1, c2, c3 = st.columns([2, 1, 1])
    nicho = c1.text_input("Nicho:", value="Utilidades Domésticas")
    ticket_sel = c2.selectbox("Ticket:", ["R$ 29 - R$ 97", "R$ 97 - R$ 297", "R$ 297+"])
    
    if st.button("🚀 Iniciar Scanner Full Data", use_container_width=True):
        with st.status("Minerando e Calculando Crescimento..."):
            p = f"Liste 30 produtos de {nicho} na Shopee BR. Formato: NOME: [n] | CALOR: [0-100] | VALOR: [R$] | CRESC: [%] | URL: [link]"
            st.session_state.res_busca = gerar_ia(p)

    if st.session_state.res_busca:
        for idx, item in enumerate(st.session_state.res_busca.split("\n")):
            if "|" in item:
                try:
                    parts = item.split("|")
                    nome = parts[0].replace("NOME:", "").strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    valor = parts[2].replace("VALOR:", "").strip()
                    cresc = parts[3].replace("CRESC:", "").strip()
                    link = parts[4].replace("URL:", "").strip()
                    
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"📦 **{nome}**")
                            st.caption(f"💰 Ticket: {valor} | 📈 Crescimento: {cresc}")
                        with col2:
                            st.write(f"🌡️ {calor}°C")
                            st.progress(min(calor/100, 1.0))
                        with col3:
                            st.write("🚀 **Status**")
                            st.markdown("🔥 `ESCALANDO`" if calor > 70 else "✅ `ESTÁVEL`")
                        with col4:
                            if st.button("Selecionar", key=f"sel_{idx}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link
                                st.toast(f"✅ {nome} no Arsenal!")
                except: continue

# --- ABA 1: ARSENAL (5 VARIAÇÕES) ---
with tabs[1]:
    st.header("⚔️ Arsenal de Vendas")
    if st.session_state.sel_nome:
        st.success(f"Alvo Selecionado: {st.session_state.sel_nome}")
        if st.button("🔥 DISPARAR 5 VARIAÇÕES"):
            with st.spinner("Gerando Munição..."):
                prompt = f"Crie 5 roteiros TikTok (Curiosidade, Dor, Medo, Prova, Transformação) para {st.session_state.sel_nome}. Separe com ###"
                variacoes = [v.strip() for v in gerar_ia(prompt).split("###") if len(v) > 10]
                for i, v in enumerate(variacoes):
                    with st.container(border=True):
                        st.subheader(f"V{i+1}")
                        st.write(v)
                        if st.button(f"Usar V{i+1}", key=f"u_{i}"):
                            st.session_state.copy_ativa = v
                            st.toast("Copiado para o Estúdio!")
    else: st.warning("Selecione no Scanner.")

# --- ABA 2: RADAR GLOBAL (EUA vs BR) ---
with tabs[2]:
    c_eua, c_br = st.columns(2)
    with c_eua:
        st.subheader("🇺🇸 Radar EUA")
        if st.button("🔍 Escanear USA"): st.info(gerar_ia("5 produtos virais TikTok USA."))
    with c_br:
        st.subheader("🇧🇷 Termômetro BR")
        if st.button("🔥 Trends Brasil"): st.success(gerar_ia("5 buscas quentes Shopee BR."))

# --- ABA 3: ESTÚDIO IA (GERAÇÃO DE MÍDIA) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod_f = st.text_input("Produto:", value=st.session_state.sel_nome)
    copy_f = st.text_area("Roteiro:", value=st.session_state.get("copy_ativa", ""))
    if st.button("🚀 Produzir Mídia (Make.com)"):
        webhook = st.secrets.get("WEBHOOK_POST_URL")
        if webhook:
            requests.post(webhook, json={"trigger": "MIDIA", "prod": prod_f, "copy": copy_f})
            st.success("Enviado para Lyria 3 & Nano Banana 2!")

# --- ABA 4: FINANCEIRO ---
with tabs[4]:
    st.header("💰 Ganhos")
    df = pd.read_csv(DATA_PATH)
    st.metric("Faturamento Total", f"R$ {df['faturamento'].sum():,.2f}")
    st.dataframe(df, use_container_width=True)
