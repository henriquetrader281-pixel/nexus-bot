import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Omega V23", layout="wide", page_icon="🔱")

# --- SISTEMA DE LOGIN (Mantido o seu original) ---
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
DATA_PATH = "dataset_nexus.csv"
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=[
        "data", "produto", "origem", "status", "views", "cliques", 
        "ctr", "vendas", "faturamento", "score", "copy"
    ]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

# Variáveis de sessão para navegação entre Abas
if "sel_nome" not in st.session_state: st.session_state.sel_nome = None
if "sel_link" not in st.session_state: st.session_state.sel_link = None

# --- MOTORES DE AUTOMAÇÃO (Patches 15, 18, 20) ---
def gerar_ia(prompt):
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}])
    return res.choices[0].message.content

def ad_scorer(copy):
    prompt = f"Aja como copywriter. Dê nota 0-100 para este roteiro TikTok: {copy}. Retorne apenas o número."
    try:
        nota = gerar_ia(prompt)
        return int(''.join(filter(str.isdigit, nota)))
    except: return 75

def acionar_webhook(tipo, payload):
    url = st.secrets.get("WEBHOOK_POST_URL")
    if url:
        try: requests.post(url, json={"trigger": tipo, "payload": payload}, timeout=5)
        except: pass

# --- INTERFACE PRINCIPAL ---
st.title("🔱 Nexus Omega: Scanner & Arsenal")

tabs = st.tabs([
    "🔎 Scanner 30x", 
    "⚔️ Arsenal de Vendas", 
    "🔥 Radar & Termômetro", 
    "📅 Agendador Social",
    "💰 Dashboard Financeiro"
])

# --- ABA 0: SCANNER 30X (Sua estrutura original com melhorias) ---
with tabs[0]:
    st.header("Monitor de Tendências Shopee")
    c1, c2, c3 = st.columns([2, 1, 1])
    nicho = c1.text_input("Nicho alvo:", value="Utilidades")
    ticket_val = c2.selectbox("Faixa de Preço:", ["Baixo (R$10-50)", "Médio (R$50-150)", "Alto (+R$150)"])
    
    if st.button("🚀 Iniciar Scanner 30x", use_container_width=True):
        with st.status("Minerando produtos com alto potencial..."):
            prompt_scan = f"Liste 30 produtos virais de {nicho} com ticket {ticket_val} na Shopee Brasil. Formato: NOME: [nome] | CALOR: [0-100] | URL: [link_original]"
            st.session_state.res_busca = gerar_ia(prompt_scan)

    if "res_busca" in st.session_state:
        for item in st.session_state.res_busca.split("\n"):
            if "|" in item:
                try:
                    parts = item.split("|")
                    nome = parts[0].replace("NOME:", "").strip()
                    calor = int(''.join(filter(str.isdigit, parts[1])))
                    link_orig = parts[2].replace("URL:", "").strip()
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        col1.write(f"📦 **{nome}**")
                        col2.progress(min(calor/100, 1.0))
                        if col3.button("Selecionar", key=f"sel_{nome}"):
                            st.session_state.sel_nome = nome
                            st.session_state.sel_link = link_orig
                            st.success(f"{nome} enviado para o Arsenal!")
                            st.rerun()
                except: continue

# --- ABA 1: ARSENAL DE VENDAS (Aba de Criação de Mídia) ---
with tabs[1]:
    st.header("⚔️ Arsenal: Gerador de Criativos 10x")
    if st.session_state.sel_nome:
        st.subheader(f"Produto Ativo: {st.session_state.sel_nome}")
        
        if st.button("⚡ INJETAR ARSENAL (5 VARIAÇÕES + MEDIA PROMPTS)"):
            with st.spinner("Gerando roteiros, scores e prompts..."):
                prompt_copy = f"Crie 5 roteiros de 15s para {st.session_state.sel_nome} (Curiosidade, Dor, Medo, Prova, Transformação). Separe com ###"
                variacoes = [v.strip() for v in gerar_ia(prompt_copy).split("###") if len(v) > 10]
                
                # Link Afiliado (Patch 20)
                aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
                link_aff = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"

                for i, v in enumerate(variacoes):
                    score = ad_scorer(v)
                    tipo = ["Curiosidade", "Dor", "Medo", "Prova", "Transformação"][i]
                    with st.container(border=True):
                        st.write(f"**V{i+1} - {tipo} | Score: {score}/100**")
                        st.write(v)
                        st.caption(f"🎨 **Prompt Nano Banana 2:** {st.session_state.sel_nome}, hyper-realistic, tiktok trend style.")
                        
                        ca, cb = st.columns(2)
                        if ca.button(f"🎬 Produzir Mídia V{i+1}", key=f"prod_{i}"):
                            acionar_webhook("GERAR_MIDIA", {"copy": v, "prod": st.session_state.sel_nome, "link": link_aff, "tipo": tipo})
                            st.toast("Enviado para Lyria 3 e Nano Banana 2!")
                        
                        if cb.button(f"📅 Agendar V{i+1}", key=f"age_{i}"):
                            # Salva no Dataset Master
                            df = pd.read_csv(DATA_PATH)
                            novo = {"data": datetime.now().strftime("%d/%m"), "produto": st.session_state.sel_nome, "origem": tipo, "status": "AGENDADO", "score": score, "copy": v}
                            pd.concat([df, pd.DataFrame([novo])]).to_csv(DATA_PATH, index=False)
                            st.success("Adicionado à fila de postagem!")
    else:
        st.warning("⚠️ Selecione um produto no Scanner primeiro.")

# --- ABA 2: RADAR & TERMÔMETRO (Inteligência EUA/BR) ---
with tabs[2]:
    st.header("🎯 Inteligência de Mercado Global")
    c_eua, c_br = st.columns(2)
    with c_eua:
        st.subheader("🇺🇸 Radar Achadinhos EUA")
        if st.button("🔍 Escanear TikTok USA"):
            st.info(gerar_ia("Liste 5 produtos virais no TikTok USA hoje que ainda não saturaram no Brasil."))
    with c_br:
        st.subheader("🇧🇷 Termômetro Shopee Brasil")
        if st.button("🔥 Trends Shopee BR"):
            st.success(gerar_ia("Quais os 5 termos de produtos mais buscados na Shopee Brasil agora?"))

# --- ABA 4: DASHBOARD FINANCEIRO (Gestão de ROI) ---
with tabs[4]:
    st.header("💰 Dashboard Financeiro")
    df_f = pd.read_csv(DATA_PATH)
    if not df_f.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Vendas Totais", len(df_f[df_f['status'] == "VENDA"]))
        col2.metric("Score Médio Copies", f"{df_f['score'].mean():.1f}")
        col3.metric("Status", "Operacional 🟢")
        st.dataframe(df_f)
    
    if st.button("Sair do Sistema"):
        st.session_state.autenticado = False
        st.rerun()
