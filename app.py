import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. SETUP ---
st.set_page_config(page_title="Nexus Absolute V17.9", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def init_dataset():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "data", "post_id", "produto", "roteiro", "link_origem", 
            "views", "cliques", "ctr", "status", "score"
        ])
        df.to_csv(DATA_PATH, index=False)

init_dataset()

# --- 2. LOGIN (Omitido para brevidade, mantenha o seu atual) ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
# ... (Mantenha seu bloco de login aqui) ...

# --- 3. MOTORES IA & NOTIFICAÇÕES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def enviar_notificacao(msg):
    url = st.secrets.get("WEBHOOK_WHATSAPP")
    if url: 
        try: requests.post(url, json={"texto": f"🔱 *NEXUS REPORT*:\n{msg}"})
        except: pass

# --- 4. INTERFACE ---
st.title("🔱 Nexus Brain: Absolute System")
tabs = st.tabs(["🔎 Mineração", "🎥 Criativos", "💬 Funil", "📊 Dataset", "⚡ Automação"])

with tabs[0]: 
    st.header("🎯 Mineração com Filtro de Preço")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        termo = st.text_input("O que buscar hoje?")
    with col2:
        # A BARRA DE PRECIFICAÇÃO QUE FALTOU
        preco_max = st.slider("Preço Máximo (R$):", 5, 200, 50)
    
    if st.button("🔄 Rodar Cruzamento", use_container_width=True):
        with st.status("Minerando produtos de baixo ticket..."):
            # A IA agora recebe a instrução de preço
            prompt_min = f"""
            Identifique 5 produtos de {termo} na Shopee Brasil.
            REGRAS:
            1. Tendência alta no Google.
            2. Preço máximo de R$ {preco_max}.
            3. Retorne uma tabela com Nome do Produto e Sugestão de Link.
            """
            res = gerar_ia(prompt_min)
            st.session_state['tabela_cruzada'] = res
            st.session_state['p_minerado'] = termo
    
    if 'tabela_cruzada' in st.session_state:
        st.markdown(st.session_state['tabela_cruzada'])

with tabs[1]: # CRIATIVOS
    prod = st.text_input("Produto alvo:", value=st.session_state.get('p_minerado', ""))
    link_raw = st.text_input("Link Original da Shopee:")
    
    if st.button("🚀 Criar Arsenal & Notificar"):
        # Lógica de clonagem de sucesso
        df_hist = pd.read_csv(DATA_PATH)
        top = df_hist[df_hist["status"] == "ESCALA"].sort_values(by="ctr", ascending=False).head(3)
        
        prompt = f"Crie 5 roteiros TikTok para {prod}. Separe com ###"
        if not top.empty:
            prompt = f"Baseado no sucesso: {top['roteiro'].to_list()}, crie 5 variações para {prod}. Separe com ###"
            
        variacoes = [v.strip() for v in gerar_ia(prompt).split("###") if len(v) > 10]
        df = pd.read_csv(DATA_PATH)
        for v in variacoes:
            novo = {"data": datetime.now().strftime("%d/%m/%Y"), "post_id": "PENDENTE", "produto": prod, "roteiro": v, "link_origem": link_raw, "views": 0, "cliques": 0, "ctr": 0, "status": "TESTE", "score": 10}
            df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("Arsenal pronto e salvo!")
        enviar_notificacao(f"Arsenal pronto para {prod}. Verifique a aba Dataset.")

# ... (Mantenha as outras abas: Funil, Dataset e Automação do script anterior) ...
