import streamlit as st
from groq import Groq
from datetime import datetime
import urllib.parse
import requests
import pandas as pd
import os

# --- 1. SETUP & DATASET ---
st.set_page_config(page_title="Nexus Absolute V19.0", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def init_dataset():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "data", "produto", "roteiro", "link_final", "status", "score"
        ])
        df.to_csv(DATA_PATH, index=False)

init_dataset()

# --- 2. MOTORES IA & WEBHOOKS ---
# Usando a chave que você pegou no console.groq.com
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def enviar_para_make(payload):
    url = st.secrets.get("WEBHOOK_POSTAGEM")
    if url:
        try: return requests.post(url, json=payload)
        except: return None

# --- 3. INTERFACE ---
st.title("🔱 Nexus Brain: Absolute System V19.0")
tabs = st.tabs(["🔎 Mineração", "🎥 Criar Arsenal", "📊 Dataset", "⚡ Automação"])

with tabs[0]: 
    st.header("🎯 Mineração de Baixo Ticket")
    col1, col2 = st.columns([2, 1])
    with col1:
        nicho = st.text_input("Qual nicho buscar hoje?", placeholder="ex: Cozinha Criativa")
    with col2:
        # BARRA DE PRECIFICAÇÃO (Essencial para sua estratégia)
        preco_max = st.slider("Preço Máximo (R$):", 5, 100, 47)
    
    if st.button("🔄 Escanear Produtos Atuais"):
        with st.status("Buscando tendências de Abril/2026..."):
            prompt = f"Sugira 5 produtos virais de {nicho} na Shopee Brasil até R${preco_max}. Retorne em tabela com nome e por que vende."
            res = gerar_ia(prompt)
            st.session_state['produtos_sugeridos'] = res
            st.markdown(res)

with tabs[1]:
    st.header("🚀 Gerador de Arsenal")
    p_nome = st.text_input("Nome do Produto Alvo:")
    p_link = st.text_input("Link da Shopee (Original ou Afiliado):")
    
    if st.button("🔥 Gerar Arsenal de Vídeos"):
        with st.spinner("IA criando roteiros de alta conversão..."):
            prompt_roteiro = f"Crie 5 roteiros curtos (estilo TikTok) para vender o produto: {p_nome}. Foque em gatilhos de escassez e preço baixo. Separe os roteiros com '---'."
            roteiros_raw = gerar_ia(prompt_roteiro)
            
            lista_roteiros = [r.strip() for r in roteiros_raw.split("---") if len(r) > 20]
            
            # Salva no Dataset
            df = pd.read_csv(DATA_PATH)
            for rot in lista_roteiros:
                novo = {
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "produto": p_nome,
                    "roteiro": rot,
                    "link_final": p_link,
                    "status": "PRONTO",
                    "score": 10
                }
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success(f"✅ Arsenal criado! {len(lista_roteiros)} roteiros salvos no Dataset.")
            st.markdown(roteiros_raw)

with tabs[3]:
    st.header("🕹️ Disparo para TikTok (Buffer)")
    df_ready = pd.read_csv(DATA_PATH)
    prontos = df_ready[df_ready["status"] == "PRONTO"]
    
    if not prontos.empty:
        st.write(f"Você tem {len(prontos)} vídeos na fila.")
        if st.button("▶️ ENVIAR PARA O TIKTOK AGORA", type="primary"):
            item = prontos.iloc[0] # Pega o primeiro da fila
            
            payload = {
                "produto": item["produto"],
                "texto": f"{item['roteiro']}\n\nLink no Comentário: {item['link_final']}",
                "data_envio": str(datetime.now())
            }
            
            res = enviar_para_make(payload)
            if res:
                # Atualiza status para não postar repetido
                df_ready.loc[prontos.index[0], "status"] = "POSTADO"
                df_ready.to_csv(DATA_PATH, index=False)
                st.success(f"🚀 Enviado para o Buffer: {item['produto']}")
            else:
                st.error("Erro ao conectar com o Make. Verifique o Webhook nos Secrets.")
    else:
        st.warning("Nenhum roteiro pronto no Arsenal para postar.")
