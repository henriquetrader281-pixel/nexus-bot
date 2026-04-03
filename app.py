import streamlit as st
from groq import Groq
import pandas as pd
import os
import random
import update  # Módulo de SEO e Escala

# Configuração da Página
st.set_page_config(page_title="Nexus Absolute V71", layout="wide", page_icon="🔱")

# --- SISTEMA DE LOGIN SEGURO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Absolute Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Insira a senha de acesso:", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if senha == "Bru2024!":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta. Acesso negado.")
    st.stop()

if not st.session_state.autenticado:
    login()

# --- INICIALIZAÇÃO PÓS-LOGIN ---
DATA_PATH = "dataset_nexus.csv"
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data", "loja", "produto", "link_afiliado", "status", "copy_funil", "horario_previsto"]).to_csv(DATA_PATH, index=False)

if "sel_nome" not in st.session_state: st.session_state.sel_nome = None
if "sel_link" not in st.session_state: st.session_state.sel_link = None
if "res_busca" not in st.session_state: st.session_state.res_busca = ""

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"ERRO_CONEXAO: {e}"

# --- INTERFACE PRINCIPAL ---
st.title("🔱 Nexus Absolute: Scanner 30x & Escala")

tabs = st.tabs(["🔎 Scanner V71", "🚀 Arsenal SEO", "📊 Performance"])

# --- ABA 0: SCANNER ---
with tabs[0]:
    st.header("Monitor de Produtos Quentes (Shopee Focus)")
    c1, c2 = st.columns([3, 1])
    nicho = c1.text_input("Nicho:", value="Utilidades Domésticas")
    ticket = c2.selectbox("Ticket:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Escanear 30 Tendências Shopee", use_container_width=True):
        with st.status("Minerando 30 produtos reais..."):
            p = f"""Liste 30 produtos virais de {nicho} ({ticket}) na Shopee Brasil.
            Responda EXATAMENTE assim para cada um:
            NOME: [nome] | TEND: [%] | CALOR: [0-100] | URL: https://shopee.com.br/item"""
            resultado = gerar_ia(p)
            if "ERRO_CONEXAO" not in resultado:
                st.session_state.res_busca = resultado
            else:
                st.error("Falha na conexão.")

    if st.session_state.res_busca:
        linhas = st.session_state.res_busca.split("\n")
        for idx, item in enumerate(linhas):
            if "|" in item and "NOME:" in item:
                try:
                    parts = item.split("|")
                    nome = parts[0].replace("NOME:", "").strip()
                    tend = parts[1].replace("TEND:", "").strip()
                    calor_str = ''.join(filter(str.isdigit, parts[2]))
                    calor_val = int(calor_str) if calor_str else 50
                    link_orig = parts[3].replace("URL:", "").strip()

                    mercado_tag = "Shopee 🟠" if "shopee" in link_orig.lower() else "Outro ⚪"

                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"📦 **{nome}**")
                            st.caption(f"🌍 Tendência: {tend}")
                            st.markdown(f"🛒 **Mercado:** {mercado_tag}")
                        with col2:
                            st.progress(min(calor_val / 100, 1.0))
                            st.write(f"🌡️ {calor_val}°C")
                        with col3:
                            if st.button("Selecionar", key=f"sel_{idx}"):
                                st.session_state.sel_nome = nome
                                st.session_state.sel_link = link_orig
                                st.toast(f"✅ {nome} enviado!")
                                st.rerun()
                except:
                    continue

# --- ABA 1: ARSENAL ---
with tabs[1]:
    st.header("🚀 Gerador de Escala 10x")
    if st.session_state.sel_nome:
        st.success(f"📦 **Produto Ativo:** {st.session_state.sel_nome}")
        if st.button("⚡ INJETAR 10 VARIAÇÕES COM SEO", type="primary"):
            with st.spinner("Processando..."):
                if update.aplicar_seo_viral(st.session_state.sel_nome, st.session_state.sel_link, nicho):
                    st.balloons()
                    st.success("🔥 Injetado no Agendador!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")

# --- ABA 2: PERFORMANCE ---
with tabs[2]:
    if st.button("Sair do Sistema"):
        st.session_state.autenticado = False
        st.rerun()
    update.dashboard_performance_simples()
    
