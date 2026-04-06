import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Omega V26", layout="wide", page_icon="🔱")

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

if not st.session_state.autenticado:
    login()

# --- INICIALIZAÇÃO DE DADOS & IA ---
DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=[
        "data", "produto", "origem", "status", "views", "cliques", 
        "ctr", "vendas", "faturamento", "score", "copy"
    ]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

# Variáveis de sessão para evitar o "reset" na mineração
if "sel_nome" not in st.session_state: st.session_state.sel_nome = None
if "sel_link" not in st.session_state: st.session_state.sel_link = None
if "res_busca" not in st.session_state: st.session_state.res_busca = ""

# --- MOTORES DE IA E WEBHOOK ---
def gerar_ia(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"system", "content": "Seja direto. Use apenas o formato solicitado."},
                      {"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    except: return "ERRO"

def acionar_webhook(tipo, payload):
    url = st.secrets.get("WEBHOOK_POST_URL")
    if url:
        requests.post(url, json={"trigger": tipo, "payload": payload})

# --- INTERFACE PRINCIPAL ---
st.title("🔱 Nexus Absolute: Scanner & Arsenal V26")

tabs = st.tabs([
    "🔎 Scanner 30x", 
    "⚔️ Arsenal de Vendas", 
    "🔥 Radar & Termômetro", 
    "🎥 Estúdio de Mídia (IA)", 
    "📅 Agendador Social", 
    "💰 Financeiro"
])

# --- ABA 0: SCANNER (CORRIGIDO) ---
with tabs[0]:
    st.header("Monitor de Tendências Massivo")
    c1, c2 = st.columns([3, 1])
    n_alvo = c1.text_input("Nicho alvo:", value="Utilidades Domésticas")
    t_alvo = c2.selectbox("Ticket Médio:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Iniciar Varredura 30x", use_container_width=True):
        with st.status("Minerando..."):
            # Prompt reforçado para evitar erros de formatação
            p = f"Liste 30 produtos virais de {n_alvo} ({t_alvo}) na Shopee BR. Responda APENAS linhas no formato: NOME: [nome] | CALOR: [0-100] | URL: [link]"
            st.session_state.res_busca = gerar_ia(p)

    if st.session_state.res_busca:
        for item in st.session_state.res_busca.split("\n"):
            if "|" in item:
                try:
                    parts = item.split("|")
                    nome = parts[0].replace("NOME:", "").strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    link = parts[2].replace("URL:", "").strip()
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        col1.write(f"📦 **{nome}**")
                        col2.progress(min(calor/100, 1.0))
                        if col3.button("Selecionar", key=f"sel_{nome}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link
                            st.toast(f"✅ {nome} enviado para o Arsenal!")
                except: continue

# --- ABA 1: ARSENAL (REINSERIDO) ---
with tabs[1]:
    st.header("⚔️ Arsenal: 5 Variações Estratégicas")
    if st.session_state.sel_nome:
        st.success(f"Produto Ativo: {st.session_state.sel_nome}")
        if st.button("🔥 DISPARAR 5 VARIAÇÕES VIRAIS"):
            with st.spinner("Gerando Munição..."):
                prompt = f"Crie 5 roteiros TikTok (Curiosidade, Dor, Medo, Prova, Transformação) para {st.session_state.sel_nome}. Separe com ###"
                variacoes = [v.strip() for v in gerar_ia(prompt).split("###") if len(v) > 10]
                
                for i, v in enumerate(variacoes):
                    with st.container(border=True):
                        st.subheader(f"Variação {i+1}")
                        st.write(v)
                        if st.button(f"Usar V{i+1} no Estúdio", key=f"use_{i}"):
                            st.session_state.copy_ativa = v
                            st.success("Enviado para Aba 'Estúdio'!")
    else:
        st.warning("Selecione um produto no Scanner.")

# --- ABA 2: RADAR & TERMÔMETRO (REINSERIDO) ---
with tabs[2]:
    c_eua, c_br = st.columns(2)
    with c_eua:
        st.subheader("🇺🇸 Radar EUA")
        if st.button("Escanear TikTok USA"):
            st.info(gerar_ia("Liste 5 produtos virais nos EUA hoje."))
    with c_br:
        st.subheader("🇧🇷 Termômetro Brasil")
        if st.button("Trends Shopee BR"):
            st.success(gerar_ia("Quais os termos mais buscados na Shopee BR agora?"))

# --- ABA 3: ESTÚDIO DE MÍDIA (IA) (REINSERIDO) ---
with tabs[3]:
    st.header("🎥 Estúdio de Mídia")
    prod = st.text_input("Produto:", value=st.session_state.sel_nome if st.session_state.sel_nome else "")
    copy = st.text_area("Roteiro Selecionado:", value=st.session_state.get("copy_ativa", ""), height=150)
    
    if st.button("🚀 Produzir Mídia Completa (Voz + Imagem)"):
        aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
        link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link if st.session_state.sel_link else '')}&aff_id={aff_id}"
        acionar_webhook("GERAR_MIDIA", {"produto": prod, "roteiro": copy, "link": link_final})
        st.success("Comando enviado para Lyria 3 e Nano Banana 2 via Make.com!")

# --- ABA 4: AGENDADOR SOCIAL ---
with tabs[4]:
    st.header("📅 Agendador")
    d_post = st.date_input("Data do Post")
    h_post = st.time_input("Horário")
    if st.button("Confirmar Agendamento"):
        st.success(f"Post de {st.session_state.sel_nome} agendado!")

# --- ABA 5: FINANCEIRO ---
with tabs[5]:
    st.header("💰 Ganhos & Performance")
    df = pd.read_csv(DATA_PATH)
    st.dataframe(df, use_container_width=True)
