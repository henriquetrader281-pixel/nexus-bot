import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO E BANCO DE DADOS ---
st.set_page_config(page_title="Nexus Absolute V17.5", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def init_dataset():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "data", "post_id", "produto", "roteiro", "link_origem", 
            "views", "cliques", "ctr", "status", "score"
        ])
        df.to_csv(DATA_PATH, index=False)

init_dataset()

# --- 2. SEGURANÇA E ACESSO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔐 Nexus Private Access</h1>", unsafe_allow_html=True)
    with st.form("login"):
        e = st.text_input("E-mail:")
        s = st.text_input("Senha:", type="password")
        if st.form_submit_button("Liberar Nexus", use_container_width=True):
            autorizados = st.secrets.get("ALLOWED_USERS", "").split(",")
            if e in [i.strip() for i in autorizados] and s == st.secrets["NEXUS_PASSWORD"]:
                st.session_state["autenticado"] = True
                st.session_state["user_email"] = e
                st.rerun()
            else: st.error("Acesso Negado.")
    st.stop()

# --- 3. MOTORES DE INTELIGÊNCIA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def enviar_notificacao(msg):
    url = st.secrets.get("WEBHOOK_WHATSAPP")
    if url: requests.post(url, json={"texto": f"🔱 *NEXUS:* {msg}"})

# --- 4. FUNÇÕES DE PERFORMANCE E ESCALA ---
def processar_metricas(df):
    df["views"] = pd.to_numeric(df["views"]).fillna(0)
    df["cliques"] = pd.to_numeric(df["cliques"]).fillna(0)
    df["ctr"] = (df["cliques"] / df["views"] * 100).fillna(0)
    # Score: 70% CTR + Bónus de Volume
    df["score"] = (df["ctr"] * 0.7) + (df["views"] * 0.001)
    
    # Atualização de Status automática
    df.loc[df["ctr"] >= 3, "status"] = "ESCALA"
    df.loc[df["ctr"] < 1, "status"] = "DESCARTADO"
    return df

def disparar_ciclo():
    df = pd.read_csv(DATA_PATH)
    # Seleciona prioridades: ESCALA primeiro, depois TESTE. Ignora score < 10.
    postagens = df[
        ((df["status"] == "ESCALA") | (df["status"] == "TESTE")) & (df["score"] >= 10)
    ].sort_values(by=["status", "ctr", "score"], ascending=False).head(4)
    
    horarios = ["08:00", "12:30", "18:00", "21:30"]
    for i, (idx, row) in enumerate(postagens.iterrows()):
        p_id = f"NEXUS_{datetime.now().strftime('%d%m')}_{i}"
        link_track = f"{row['link_origem']}?src={p_id}"
        
        payload = {
            "post_id": p_id, "produto": row['produto'], 
            "roteiro": row['roteiro'], "link": link_track, "hora": horarios[i]
        }
        requests.post(st.secrets["WEBHOOK_POSTAGEM"], json=payload)
        enviar_notificacao(f"Post agendado: {row['produto']} ({horarios[i]})")
    st.success("Ciclo de 4 posts enviado!")

# --- 5. INTERFACE ---
st.title("🔱 Nexus Brain: Absolute Decision")
tabs = st.tabs(["🔎 Mineração", "🎥 Criativos", "📊 Dataset", "⚡ Automação"])

with tabs[0]: # MINERAÇÃO CRUZADA
    termo = st.text_input("Tendência para hoje:")
    if st.button("🔄 Rodar Cruzamento"):
        res = gerar_ia(f"Liste 5 variações de {termo} na Shopee com alta busca no Google. Retorne em tabela.")
        st.markdown(res)
        st.session_state['p_minerado'] = termo

with tabs[1]: # GERAÇÃO E CLONAGEM
    prod = st.text_input("Produto:", value=st.session_state.get('p_minerado', ""))
    link = st.text_input("Link Shopee:")
    
    if st.button("🚀 Criar Arsenal (Baseado em Sucesso)"):
        df_hist = pd.read_csv(DATA_PATH)
        top = df_hist[df_hist["status"] == "ESCALA"].sort_values(by="ctr", ascending=False).head(5)
        
        prompt = f"Crie 5 novos roteiros para {prod}."
        if not top.empty:
            prompt = f"Baseado nestes sucessos: {top['roteiro'].to_list()}, crie 5 novos para {prod} mantendo o padrão."
            
        variacoes = [v.strip() for v in gerar_ia(prompt).split("###") if len(v) > 10]
        df = pd.read_csv(DATA_PATH)
        for v in variacoes:
            novo = {
                "data": datetime.now().strftime("%d/%m/%Y"), "produto": prod, "roteiro": v,
                "link_origem": link, "views": 0, "cliques": 0, "ctr": 0, "status": "TESTE", "score": 10
            }
            df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("Roteiros salvos!")

with tabs[2]: # GESTÃO DE DADOS
    df_raw = pd.read_csv(DATA_PATH)
    # Limpa descartados da visualização para focar no lucro
    df_view = df_raw[df_raw["status"] != "DESCARTADO"]
    edited = st.data_editor(df_view, num_rows="dynamic")
    if st.button("💾 Atualizar e Limpar"):
        df_final = processar_metricas(edited)
        df_final.to_csv(DATA_PATH, index=False)
        st.rerun()

with tabs[3]: # PAINEL DE CONTROLO PLAY/STOP
    st.header("🕹️ Estado do Sistema")
    if "nexus_active" not in st.session_state: st.session_state["nexus_active"] = False
    
    c1, c2 = st.columns(2)
    if c1.button("▶️ PLAY", use_container_width=True, type="primary"):
        st.session_state["nexus_active"] = True
        enviar_notificacao("ONLINE")
    if c2.button("🛑 STOP", use_container_width=True):
        st.session_state["nexus_active"] = False
        enviar_notificacao("OFFLINE")
        
    if st.session_state["nexus_active"]:
        st.success("Robô monitorando métricas.")
        if st.button("🚀 Forçar Disparo"): disparar_ciclo()
    else:
        st.error("Automação desligada.")
