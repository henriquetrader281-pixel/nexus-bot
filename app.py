import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP ---
st.set_page_config(page_title="Nexus Absolute V22.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["data", "produto", "roteiro", "link", "status"]).to_csv(DATA_PATH, index=False)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def log_sistema(mensagem):
    if 'logs' not in st.session_state: st.session_state.logs = []
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {mensagem}")

def gerar_ia(prompt):
    log_sistema("Consultando Cérebro Groq...")
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE ---
st.sidebar.title("🛠️ Logs do Sistema")
if st.sidebar.button("Limpar Logs"): st.session_state.logs = []
if 'logs' in st.session_state:
    for log in reversed(st.session_state.logs[-10:]): st.sidebar.caption(log)

st.title("🔱 Nexus Brain: Absolute System V22.0")
tabs = st.tabs(["🌎 Inteligência Global", "🎥 Arsenal & Espião", "⚡ Automação"])

with tabs[0]:
    st.header("🎯 Termômetro de Mercado")
    col1, col2 = st.columns([2, 1])
    with col1: nicho = st.text_input("Nicho:", placeholder="Ex: Cozinha, Tech")
    with col2: v_max = st.slider("Preço Máximo (R$):", 5, 250, 47)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔥 Quentes no BRASIL"):
            st.markdown(gerar_ia(f"5 produtos de {nicho} virais na Shopee BR até R${v_max}. Tabela."))
    with c2:
        if st.button("🇺🇸 Quentes nos EUA"):
            st.markdown(gerar_ia(f"5 trends de {nicho} no TikTok USA hoje abaixo de $20."))

with tabs[1]:
    st.header("🚀 Arsenal & Modo Espião")
    col_a, col_b = st.columns(2)
    with col_a:
        p_nome = st.text_input("Nome do Produto:")
        p_link_raw = st.text_input("Link Shopee:")
    with col_b:
        espinha = st.text_area("Script do Concorrente (Opcional):", placeholder="Cole aqui o que o concorrente disse no vídeo dele...")

    if st.button("🔥 Gerar Arsenal"):
        if p_nome and p_link_raw:
            log_sistema(f"Iniciando Arsenal para {p_nome}")
            my_id = st.secrets.get("SHOPEE_ID", "AGUARDANDO")
            link_afiliado = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link_raw)}&aff_id={my_id}"
            
            contexto = f"Baseado neste script de concorrente: {espinha}" if espinha else "Estilo achadinho viral."
            prompt = f"Crie 5 roteiros de TikTok para {p_nome}. {contexto}. Separe por '---'."
            
            roteiros = gerar_ia(prompt).split("---")
            df = pd.read_csv(DATA_PATH)
            novos = []
            for r in roteiros:
                if len(r) > 10:
                    novos.append({"data": datetime.now().strftime("%d/%m %H:%M"), "produto": p_nome, "roteiro": r.strip(), "link": link_afiliado, "status": "FILA"})
            
            pd.concat([df, pd.DataFrame(novos)], ignore_index=True).to_csv(DATA_PATH, index=False)
            st.success("✅ Arsenal salvo!")
            if "WEBHOOK_WHATSAPP" in st.secrets:
                requests.post(st.secrets["WEBHOOK_WHATSAPP"], json={"texto": f"🔱 NOVO ARSENAL: {p_nome}"})

with tabs[2]:
    st.header("🕹️ Automação")
    df_ver = pd.read_csv(DATA_PATH)
    fila = df_ver[df_ver["status"] == "FILA"]
    st.metric("Fila", len(fila))
    
    if not fila.empty and st.button("▶️ POSTAR AGORA", type="primary"):
        item = fila.iloc[0]
        payload = {"texto": f"{item['roteiro']}\n\n🛒 Link: {item['link']}", "produto": item["produto"]}
        resp = requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
        if resp.status_code == 200:
            df_ver.loc[fila.index[0], "status"] = "POSTADO"
            df_ver.to_csv(DATA_PATH, index=False)
            st.success("🚀 Enviado!")
            log_sistema(f"Postagem realizada: {item['produto']}")

# --- 3. SEÇÃO DE PATCHES ---
def patch_01(): pass # Espaço para melhoria de SEO
def patch_02(): pass # Espaço para integração com Instagram
def patch_03(): pass
def patch_04(): pass
def patch_05(): pass
def patch_06(): pass
def patch_07(): pass
def patch_08(): pass
def patch_09(): pass
def patch_10(): pass
