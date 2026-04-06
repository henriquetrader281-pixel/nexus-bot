import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. CONFIG & DATASET (Core & Patches 25, 29) ---
st.set_page_config(page_title="Nexus Omega: Full Automation", layout="wide", page_icon="🔱")

DATA_PATH = "nexus_master_data.csv"
if not os.path.exists(DATA_PATH):
    df = pd.DataFrame(columns=[
        "data", "produto", "origem", "status", "views", "cliques", 
        "ctr", "vendas", "faturamento", "score", "agendamento", "copy"
    ])
    df.to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Variáveis de Sessão para Seleção de Produto
if "sel_nome" not in st.session_state: st.session_state.sel_nome = ""
if "sel_link" not in st.session_state: st.session_state.sel_link = ""

# --- 2. MOTORES DE IA E CONECTIVIDADE ---

def gerar_ia(prompt):
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}]).choices[0].message.content

def acionar_automacao_total(tipo, dados):
    webhook = st.secrets.get("WEBHOOK_POST_URL")
    if webhook:
        payload = {"nexus_trigger": tipo, "timestamp": str(datetime.now()), "payload": dados}
        try: requests.post(webhook, json=payload, timeout=5)
        except: pass

def ad_scorer(roteiro):
    nota = gerar_ia(f"Dê nota 0-100 para este roteiro TikTok: {roteiro}. Retorne apenas o número.")
    return int(''.join(filter(str.isdigit, nota))) if any(c.isdigit() for c in nota) else 70

# --- 3. INTERFACE DE COMANDO ---
st.title("🔱 Nexus Brain: Absolute Omega 2026")

tabs = st.tabs([
    "🔎 Scanner 30x", 
    "⚔️ Arsenal de Vendas",
    "🔥 Radar & Termômetro", 
    "🎥 Estúdio de Mídia (IA)", 
    "📅 Agendador Social", 
    "💰 Dashboard Financeiro", 
    "📊 Dataset Master"
])

# --- ABA 0: SCANNER 30X (O QUE FALTAVA) ---
with tabs[0]:
    st.header("🔎 Scanner de Tendências Massivo")
    c1, c2, c3 = st.columns([2, 1, 1])
    nicho = c1.text_input("Nicho alvo:", "Utilidades Domésticas")
    ticket = c2.selectbox("Ticket Médio:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Iniciar Varredura 30x", use_container_width=True):
        with st.status("Minerando..."):
            res = gerar_ia(f"Liste 30 produtos de {nicho} na Shopee Brasil. Formato: NOME: [nome] | CALOR: [0-100] | URL: [link]")
            st.session_state.res_busca = res

    if "res_busca" in st.session_state:
        for item in st.session_state.res_busca.split("\n"):
            if "|" in item:
                try:
                    p = item.split("|")
                    nome = p[0].replace("NOME:", "").strip()
                    calor = int(''.join(filter(str.isdigit, p[1])))
                    link = p[2].replace("URL:", "").strip()
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        col1.write(f"📦 **{nome}**")
                        col2.progress(min(calor/100, 1.0))
                        if col3.button("Selecionar", key=f"sel_{nome}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link
                            st.toast(f"✅ {nome} pronto para o Arsenal!")
                except: continue

# --- ABA 1: ARSENAL DE VENDAS (5 VARIAÇÕES) ---
with tabs[1]:
    st.header("⚔️ Arsenal de Copies & Ganchos")
    if st.session_state.sel_nome:
        st.info(f"Produto Selecionado: {st.session_state.sel_nome}")
        if st.button("🔥 GERAR 5 VARIAÇÕES VIRAIS"):
            with st.spinner("Criando munição..."):
                prompt = f"Crie 5 roteiros TikTok de 15s para {st.session_state.sel_nome} (Ângulos: Curiosidade, Dor, Medo, Prova, Transformação). Separe com ###"
                variacoes = [v.strip() for v in gerar_ia(prompt).split("###") if len(v) > 10]
                
                for i, v in enumerate(variacoes):
                    score = ad_scorer(v)
                    with st.container(border=True):
                        st.subheader(f"V{i+1} | Score: {score}")
                        st.write(v)
                        if st.button(f"Usar V{i+1} no Estúdio", key=f"use_{i}"):
                            st.session_state.copy_ativa = v
                            st.session_state.score_ativo = score
                            st.success("Enviado para Aba 'Estúdio de Mídia'!")
    else:
        st.warning("Selecione um produto no Scanner primeiro.")

# --- ABA 2: RADAR & TERMÔMETRO (Mantido) ---
with tabs[2]:
    st.header("🎯 Inteligência de Mercado Global")
    c_eua, c_br = st.columns(2)
    with c_eua:
        st.subheader("🇺🇸 Radar Achadinhos EUA")
        if st.button("🔍 Escanear TikTok/Amazon USA"):
            st.info(gerar_ia("Liste 5 produtos virais nos EUA hoje."))
    with c_br:
        st.subheader("🇧🇷 Termômetro Shopee Brasil")
        if st.button("🔥 Escanear Trends Shopee BR"):
            st.success(gerar_ia("5 termos mais buscados na Shopee BR agora."))

# --- ABA 3: ESTÚDIO DE MÍDIA (IA) (Mantido + Score) ---
with tabs[3]:
    st.header("🎥 Produção de Criativos (IA)")
    p_estudio = st.text_input("Nome:", value=st.session_state.sel_nome)
    l_estudio = st.text_input("Link:", value=st.session_state.sel_link)
    copy_estudio = st.text_area("Roteiro:", value=st.session_state.get("copy_ativa", ""))

    if st.button("🚀 DISPARAR PRODUÇÃO COMPLETA"):
        with st.status("Acionando motores..."):
            aff_link = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(l_estudio)}&aff_id={st.secrets.get('SHOPEE_ID')}"
            dados = {"produto": p_estudio, "roteiro": copy_estudio, "link": aff_link}
            acionar_automacao_total("GERAR_MIDIA", dados)
            st.success("Enviado para Lyria 3 e Nano Banana 2 via Webhook!")

# --- ABA 4: AGENDADOR SOCIAL (Mantido) ---
with tabs[4]:
    st.header("📅 Agendador")
    p_agenda = st.text_input("Produto:", value=st.session_state.sel_nome)
    data_p = st.date_input("Data")
    hora_p = st.time_input("Hora")
    if st.button("Confirmar Agendamento"):
        acionar_automacao_total("AGENDAR_POST", {"prod": p_agenda, "data": str(data_p)})
        st.success("Agendado!")

# --- ABA 5: DASHBOARD FINANCEIRO (Mantido) ---
with tabs[5]:
    st.header("💰 Gestão de Ganhos")
    df_f = pd.read_csv(DATA_PATH)
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento", f"R$ {df_f['faturamento'].sum():,.2f}")
    col2.metric("Vendas", int(df_f['vendas'].sum()))
    st.line_chart(df_f.set_index("data")["faturamento"])

# --- ABA 6: DATASET MASTER (Mantido) ---
with tabs[6]:
    st.header("📊 Base de Dados Master")
    st.dataframe(pd.read_csv(DATA_PATH), use_container_width=True)
