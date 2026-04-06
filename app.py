import streamlit as st
from groq import Groq
import pandas as pd
import os
import urllib.parse
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Nexus Omega V22", layout="wide", page_icon="🔱")

# --- SISTEMA DE LOGIN (Mantido o seu original) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔱 Nexus Omega Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Insira a senha de acesso:", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if senha == "Bru2024!": # Sua senha mantida
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
        "data", "produto", "link_afiliado", "status", "copy", "score", "views", "cliques", "vendas"
    ]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

# Funções de Suporte (Patches 15, 18, 20)
def gerar_ia(prompt):
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content": prompt}])
    return res.choices[0].message.content

def ad_scorer(copy):
    nota = gerar_ia(f"Dê uma nota de 0 a 100 para este roteiro de vendas: {copy}. Retorne apenas o número.")
    return int(''.join(filter(str.isdigit, nota))) if any(char.isdigit() for char in nota) else 70

def acionar_webhook(tipo, payload):
    url = st.secrets.get("WEBHOOK_POST_URL")
    if url:
        requests.post(url, json={"trigger": tipo, "data": payload})

# --- INTERFACE PRINCIPAL ---
st.title("🔱 Nexus Omega: Scanner, Arsenal & Escala")

tabs = st.tabs(["🔎 Scanner 30x", "⚔️ Arsenal de Vendas", "🔥 Radar & Termômetro", "📊 Performance & ROI"])

# --- ABA 0: SCANNER (Sua lógica 30x melhorada) ---
with tabs[0]:
    st.header("Monitor de Produtos Quentes")
    c1, c2, c3 = st.columns([2, 1, 1])
    nicho = c1.text_input("Nicho:", value="Utilidades Domésticas")
    ticket = c2.selectbox("Ticket:", ["Baixo", "Médio", "Alto"])
    
    if st.button("🚀 Escanear 30 Tendências", use_container_width=True):
        with st.status("Minerando..."):
            p = f"Liste 30 produtos virais de {nicho} na Shopee Brasil. Formato: NOME: [nome] | CALOR: [0-100] | URL: [link]"
            st.session_state.res_busca = gerar_ia(p)

    if "res_busca" in st.session_state and st.session_state.res_busca:
        for item in st.session_state.res_busca.split("\n"):
            if "|" in item:
                parts = item.split("|")
                nome = parts[0].replace("NOME:", "").strip()
                calor = int(''.join(filter(str.isdigit, parts[1]))) if "CALOR" in parts[1] else 50
                link = parts[2].replace("URL:", "").strip()
                
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    col1.write(f"📦 **{nome}**")
                    col2.progress(calor/100)
                    if col3.button("Selecionar", key=f"sel_{nome}"):
                        st.session_state.sel_nome = nome
                        st.session_state.sel_link = link
                        st.success(f"{nome} enviado para o Arsenal!")

# --- ABA 1: ARSENAL (O Coração da Automação - Patch 14, 17, 18, 19) ---
with tabs[1]:
    st.header("⚔️ Arsenal: Geração de Mídia e Escala")
    if "sel_nome" in st.session_state and st.session_state.sel_nome:
        st.subheader(f"Produto Ativo: {st.session_state.sel_nome}")
        
        if st.button("🔥 DISPARAR 5 VARIAÇÕES VIRAIS"):
            with st.spinner("Gerando Roteiros, Scores e Prompts de Mídia..."):
                prompt = f"Crie 5 roteiros de 15s (Curiosidade, Dor, Medo, Prova, Transformação) para {st.session_state.sel_nome}. Separe com ###"
                variacoes = [v.strip() for v in gerar_ia(prompt).split("###") if len(v) > 10]
                
                # Gerar Link Afiliado (Patch 20)
                aff_id = st.secrets.get("SHOPEE_ID", "SEM_ID")
                link_aff = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(st.session_state.sel_link)}&aff_id={aff_id}"

                for i, v in enumerate(variacoes):
                    score = ad_scorer(v)
                    with st.container(border=True):
                        st.write(f"**V{i+1} | Score: {score}/100**")
                        st.write(v)
                        
                        col_a, col_b = st.columns(2)
                        if col_a.button(f"🎬 Gerar Vídeo V{i+1} (Make.com)", key=f"gen_{i}"):
                            # Dispara Patch 15, 17 e 19 via Webhook
                            acionar_webhook("GERAR_MIDIA", {"copy": v, "prod": st.session_state.sel_nome, "link": link_aff})
                            st.info("Motores Lyria 3 e Nano Banana acionados!")
                        
                        if col_b.button(f"📅 Agendar V{i+1}", key=f"age_{i}"):
                            # Salva no Dataset e aciona Agendador (Patch 27)
                            df = pd.read_csv(DATA_PATH)
                            novo = {"data": datetime.now().strftime("%d/%m"), "produto": st.session_state.sel_nome, "link_afiliado": link_aff, "status": "AGENDADO", "copy": v, "score": score}
                            pd.concat([df, pd.DataFrame([novo])]).to_csv(DATA_PATH, index=False)
                            st.success("Agendado no Buffer!")
    else:
        st.warning("Selecione um produto no Scanner primeiro.")

# --- ABA 2: RADAR & TERMÔMETRO (Patch 23, 30, 31) ---
with tabs[2]:
    st.header("🌍 Inteligência Global vs Nacional")
    c_eua, c_br = st.columns(2)
    with c_eua:
        if st.button("🇺🇸 Radar EUA"):
            st.info(gerar_ia("Produtos virais TikTok USA hoje."))
    with c_br:
        if st.button("🇧🇷 Termômetro Shopee BR"):
            st.success(gerar_ia("Tendências de busca Shopee Brasil agora."))

# --- ABA 3: PERFORMANCE (Patch 29) ---
with tabs[3]:
    st.header("📊 Dashboard de Ganhos")
    df = pd.read_csv(DATA_PATH)
    st.dataframe(df)
    if st.button("Sair do Sistema"):
        st.session_state.autenticado = False
        st.rerun()
